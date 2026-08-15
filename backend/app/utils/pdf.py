"""Shipping label PDF generation (100mm x 150mm thermal label format)."""

import io
from datetime import datetime

import barcode
from barcode.writer import SVGWriter

from app.models.order import Order


def generate_barcode_svg(code: str) -> str:
    """Generate a Code128 barcode as inline SVG string."""
    code128 = barcode.get_barcode_class("code128")
    writer = SVGWriter()
    bc = code128(code, writer=writer)
    buffer = io.BytesIO()
    bc.write(buffer, options={"module_width": 0.3, "module_height": 8, "quiet_zone": 2})
    svg_bytes = buffer.getvalue()
    return svg_bytes.decode("utf-8")


def generate_label_html(order: Order, tracking_number: str | None = None) -> str:
    """Generate HTML for a single 100x150mm shipping label."""
    address = order.shipping_address or {}
    barcode_value = tracking_number or order.order_number
    barcode_svg = generate_barcode_svg(barcode_value)

    items_summary = ", ".join(
        f"{item.product_name_snapshot} x{item.quantity}" for item in order.items
    )

    return f"""
    <div class="label">
        <div class="header">
            <div class="logo">PHOENIX</div>
            <div class="source">{order.source.value.upper()}</div>
        </div>

        <div class="barcode">
            {barcode_svg}
            <div class="tracking">{barcode_value}</div>
        </div>

        <div class="section">
            <div class="label-title">TO:</div>
            <div class="name">{address.get('full_name', '')}</div>
            <div>{address.get('street', '')}</div>
            <div>{address.get('city', '')}, {address.get('province', '')}</div>
            <div>{address.get('postal_code', '')}</div>
            <div class="phone">{address.get('phone', '')}</div>
        </div>

        <div class="section">
            <div class="label-title">ORDER:</div>
            <div>{order.order_number}</div>
            <div class="items">{items_summary}</div>
        </div>

        <div class="footer">
            <div>Courier: {(order.courier or 'N/A').upper()}</div>
            <div>{datetime.now().strftime('%d %b %Y %H:%M')}</div>
        </div>
    </div>
    """


def generate_labels_pdf(
    orders: list[Order],
    tracking_numbers: dict[int, str] | None = None,
) -> bytes:
    """Generate a multi-page PDF with one label per page (100x150mm).

    Args:
        orders: List of orders to generate labels for
        tracking_numbers: Optional dict mapping order.id to tracking number

    Returns:
        PDF bytes
    """
    from weasyprint import HTML

    tracking_numbers = tracking_numbers or {}

    labels_html = ""
    for order in orders:
        tracking = tracking_numbers.get(order.id, order.order_number)
        labels_html += generate_label_html(order, tracking)

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{
                size: 100mm 150mm;
                margin: 3mm;
            }}
            body {{
                font-family: Arial, Helvetica, sans-serif;
                font-size: 10px;
                margin: 0;
                padding: 0;
            }}
            .label {{
                page-break-after: always;
                width: 94mm;
                height: 144mm;
                padding: 2mm;
                box-sizing: border-box;
            }}
            .label:last-child {{
                page-break-after: avoid;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid #000;
                padding-bottom: 3mm;
                margin-bottom: 3mm;
            }}
            .logo {{
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 2px;
            }}
            .source {{
                font-size: 9px;
                padding: 1mm 3mm;
                border: 1px solid #000;
                border-radius: 2mm;
            }}
            .barcode {{
                text-align: center;
                margin: 3mm 0;
            }}
            .barcode svg {{
                width: 80mm;
                height: 15mm;
            }}
            .tracking {{
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 1px;
                margin-top: 1mm;
            }}
            .section {{
                border-top: 1px dashed #999;
                padding: 3mm 0;
            }}
            .label-title {{
                font-size: 8px;
                font-weight: bold;
                color: #666;
                text-transform: uppercase;
                margin-bottom: 1mm;
            }}
            .name {{
                font-size: 13px;
                font-weight: bold;
            }}
            .phone {{
                margin-top: 1mm;
            }}
            .items {{
                font-size: 9px;
                color: #444;
                margin-top: 1mm;
            }}
            .footer {{
                display: flex;
                justify-content: space-between;
                border-top: 1px solid #000;
                padding-top: 2mm;
                margin-top: auto;
                font-size: 9px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        {labels_html}
    </body>
    </html>
    """

    pdf_bytes = HTML(string=full_html).write_pdf()
    return pdf_bytes
