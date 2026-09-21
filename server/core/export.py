# server/core/export.py
"""Export laporan ke Excel & HTML."""
import io
from datetime import datetime
from pathlib import Path

import pandas as pd


def export_to_excel(df: pd.DataFrame, title: str = "Laporan") -> bytes:
    """
    Export DataFrame ke Excel dengan styling.

    Returns:
        bytes Excel file
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet utama
        df.to_excel(writer, sheet_name='Data', index=False, startrow=3)

        workbook = writer.book
        worksheet = writer.sheets['Data']

        # Format
        title_fmt = workbook.add_format({
            'bold': True, 'font_size': 16, 'font_color': '#0d6efd',
        })
        subtitle_fmt = workbook.add_format({
            'italic': True, 'font_size': 10, 'font_color': '#64748b',
        })
        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#1e293b', 'font_color': '#ffffff',
            'border': 1, 'align': 'center', 'valign': 'vcenter',
        })
        cell_fmt = workbook.add_format({
            'border': 1, 'align': 'center',
        })

        # Write title
        worksheet.merge_range('A1:H1', title, title_fmt)
        worksheet.merge_range(
            'A2:H2',
            f'Generated: {datetime.now().strftime("%d %B %Y %H:%M WIB")}',
            subtitle_fmt,
        )

        # Header styling
        for col_num, col_name in enumerate(df.columns):
            worksheet.write(3, col_num, col_name.upper(), header_fmt)

        # Auto-width columns
        for i, col in enumerate(df.columns):
            max_len = max(
                df[col].astype(str).map(len).max() if len(df) > 0 else 0,
                len(str(col))
            ) + 2
            worksheet.set_column(i, i, min(max_len, 40), cell_fmt)

        # Conditional formatting untuk PFVI score
        if 'pfvi_score' in df.columns:
            pfvi_col_idx = list(df.columns).index('pfvi_score')
            pfvi_range = f'{chr(65 + pfvi_col_idx)}5:{chr(65 + pfvi_col_idx)}{len(df) + 4}'

            worksheet.conditional_format(pfvi_range, {
                'type': 'cell', 'criteria': '>=', 'value': 65,
                'format': workbook.add_format({'bg_color': '#fecaca', 'font_color': '#991b1b', 'bold': True}),
            })
            worksheet.conditional_format(pfvi_range, {
                'type': 'cell', 'criteria': 'between', 'minimum': 40, 'maximum': 64,
                'format': workbook.add_format({'bg_color': '#fef3c7', 'font_color': '#92400e', 'bold': True}),
            })
            worksheet.conditional_format(pfvi_range, {
                'type': 'cell', 'criteria': '<', 'value': 40,
                'format': workbook.add_format({'bg_color': '#d1fae5', 'font_color': '#065f46', 'bold': True}),
            })

    return output.getvalue()


def export_to_html(df: pd.DataFrame, title: str = "Laporan") -> str:
    """Export ke HTML untuk print-to-PDF."""
    rows_html = ""
    for _, row in df.iterrows():
        cells = ""
        for col in df.columns:
            val = row[col]
            style = ""

            if col == 'pfvi_score' or col == 'PFVI':
                try:
                    v = float(val)
                    if v >= 65:
                        style = "background:#fecaca;color:#991b1b;font-weight:700;"
                    elif v >= 40:
                        style = "background:#fef3c7;color:#92400e;font-weight:700;"
                    else:
                        style = "background:#d1fae5;color:#065f46;font-weight:700;"
                except Exception:
                    pass

            if col == 'status' or col == 'Status':
                if 'BAHAYA' in str(val):
                    style = "color:#dc2626;font-weight:700;"
                elif 'SIAGA' in str(val):
                    style = "color:#d97706;font-weight:700;"
                elif 'AMAN' in str(val):
                    style = "color:#059669;font-weight:700;"

            cells += f'<td style="{style}">{val}</td>'
        rows_html += f'<tr>{cells}</tr>'

    headers = "".join([f'<th>{c}</th>' for c in df.columns])

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
    body {{ font-family: 'Segoe UI', sans-serif; padding: 30px; color: #0f172a; }}
    h1 {{ color: #0d6efd; border-bottom: 3px solid #0d6efd; padding-bottom: 10px; }}
    .meta {{ color: #64748b; font-size: 12px; margin-bottom: 20px; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
    th {{ background: #1e293b; color: white; padding: 10px; text-align: left; }}
    td {{ padding: 8px; border: 1px solid #e2e8f0; }}
    tr:nth-child(even) {{ background: #f8fafc; }}
    .footer {{ margin-top: 30px; font-size: 10px; color: #94a3b8; text-align: center; }}
    @media print {{
        body {{ padding: 10px; }}
        h1 {{ font-size: 20px; }}
    }}
</style>
</head>
<body>
    <h1>🔥 {title}</h1>
    <div class="meta">
        Platform GambutFR — Monitoring Risiko Kebakaran Lahan Gambut<br>
        Generated: {datetime.now().strftime("%d %B %Y %H:%M WIB")} • Total: {len(df)} baris
    </div>
    <table>
        <thead><tr>{headers}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    <div class="footer">
        © 2026 GambutFR — Peat Fire Risk Monitoring Platform<br>
        Data source: Kemendagri 2025, NASA FIRMS, dan input lapangan
    </div>
</body>
</html>"""