from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.http import HttpResponse
from .models import Customer, Sale, SaleItem, Payment
from .serializers import (
    CustomerSerializer, SaleSerializer, SaleListSerializer,
    SaleItemSerializer, PaymentSerializer
)
from inventory.models import InventoryItem, StockMovement


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'phone', 'email']
    ordering = ['name']


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.select_related('customer', 'created_by').prefetch_related(
        'items__inventory_item__product', 'payments'
    ).all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['payment_status', 'payment_method', 'customer']
    search_fields = ['invoice_number', 'customer__name']
    ordering_fields = ['sale_date', 'total_amount', 'created_at']
    ordering = ['-sale_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return SaleListSerializer
        return SaleSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add an item to a sale and auto-reduce inventory."""
        sale = self.get_object()
        serializer = SaleItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        inventory_item = serializer.validated_data['inventory_item']
        quantity = serializer.validated_data['quantity']

        # Check stock availability
        if inventory_item.quantity_in_stock < quantity:
            return Response(
                {'error': f'Insufficient stock. Available: {inventory_item.quantity_in_stock} {inventory_item.product.unit}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save sale item
        sale_item = serializer.save(sale=sale)

        # Auto-reduce inventory
        inventory_item.quantity_in_stock -= quantity
        inventory_item.save()

        # Record stock movement
        StockMovement.objects.create(
            inventory_item=inventory_item,
            movement_type='out',
            reason='sale',
            quantity=quantity,
            reference=sale.invoice_number,
            notes=f'Sale to {sale.customer.name if sale.customer else "walk-in customer"}',
            created_by=request.user
        )

        # Update sale total
        sale.total_amount += sale_item.total_price
        sale.save()

        return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_payment(self, request, pk=None):
        """Record a payment for a sale."""
        sale = self.get_object()
        serializer = PaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        payment = serializer.save(sale=sale, created_by=request.user)
        sale.refresh_from_db()

        return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def invoice(self, request, pk=None):
        """Generate PDF invoice for a sale."""
        sale = self.get_object()
        pdf = generate_invoice_pdf(sale)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{sale.invoice_number}.pdf"'
        return response

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Sales statistics."""
        stats = {
            'total_sales': self.queryset.count(),
            'total_revenue': self.queryset.aggregate(total=Sum('total_amount'))['total'] or 0,
            'total_collected': self.queryset.aggregate(total=Sum('amount_paid'))['total'] or 0,
            'pending_payment': self.queryset.filter(payment_status='pending').count(),
            'partial_payment': self.queryset.filter(payment_status='partial').count(),
        }
        return Response(stats)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('sale', 'created_by').all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['payment_method', 'sale']
    ordering = ['-payment_date']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


def generate_invoice_pdf(sale):
    """Generate a PDF invoice using reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    import io

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle('title', parent=styles['Title'], alignment=TA_CENTER, fontSize=20)
    elements.append(Paragraph("TIMBERFLOW", title_style))
    elements.append(Paragraph("Timber Processing & Sales", styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))

    # Invoice details
    elements.append(Paragraph(f"<b>Invoice #:</b> {sale.invoice_number}", styles['Normal']))
    elements.append(Paragraph(f"<b>Date:</b> {sale.sale_date}", styles['Normal']))
    elements.append(Paragraph(f"<b>Customer:</b> {sale.customer.name if sale.customer else 'Walk-in'}", styles['Normal']))
    if sale.customer:
        elements.append(Paragraph(f"<b>Phone:</b> {sale.customer.phone}", styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))

    # Items table
    table_data = [['Product', 'Qty', 'Unit', 'Unit Price', 'Total']]
    for item in sale.items.all():
        table_data.append([
            item.inventory_item.product.name,
            str(item.quantity),
            item.inventory_item.product.unit,
            f"KES {item.unit_price:,.2f}",
            f"KES {item.total_price:,.2f}",
        ])

    table = Table(table_data, colWidths=[7*cm, 2*cm, 2.5*cm, 3*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5*cm))

    # Totals
    right_style = ParagraphStyle('right', parent=styles['Normal'], alignment=TA_RIGHT)
    elements.append(Paragraph(f"<b>Total Amount: KES {sale.total_amount:,.2f}</b>", right_style))
    elements.append(Paragraph(f"Amount Paid: KES {sale.amount_paid:,.2f}", right_style))
    elements.append(Paragraph(f"<b>Balance: KES {sale.balance:,.2f}</b>", right_style))
    elements.append(Spacer(1, 0.5*cm))

    # Payment status
    elements.append(Paragraph(f"Payment Status: <b>{sale.get_payment_status_display()}</b>", styles['Normal']))

    # Payments history
    payments = sale.payments.all()
    if payments:
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph("<b>Payment History:</b>", styles['Normal']))
        pay_data = [['Date', 'Method', 'Reference', 'Amount']]
        for p in payments:
            pay_data.append([
                str(p.payment_date),
                p.get_payment_method_display(),
                p.reference or '-',
                f"KES {p.amount:,.2f}",
            ])
        pay_table = Table(pay_data, colWidths=[3*cm, 3*cm, 6*cm, 3*cm])
        pay_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(pay_table)

    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph("Thank you for your business!", styles['Normal']))

    doc.build(elements)
    return buffer.getvalue()
