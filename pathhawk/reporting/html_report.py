"""
Professional HTML report generation for PathHawk.
Developed by ISHA SONARIA.
"""

from datetime import datetime, timezone
import html
from pathlib import Path
from typing import List

from pathhawk import __author__, __organization__, __tagline__, __title__, __version__
from pathhawk.config import ScanConfig, ScanResult


def generate_html_report(config: ScanConfig, results: List[ScanResult], output_path: Path) -> Path:
    """Generate a responsive, dark-mode cybersecurity audit report in HTML."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    status_counts = {}
    for r in results:
        status_counts[r.status_code] = status_counts.get(r.status_code, 0) + 1

    rows_html = []
    for idx, r in enumerate(results, start=1):
        # Badge color based on status code
        if 200 <= r.status_code < 300:
            badge_cls = "badge-success"
        elif 300 <= r.status_code < 400:
            badge_cls = "badge-info"
        elif r.status_code in (401, 403):
            badge_cls = "badge-warning"
        else:
            badge_cls = "badge-danger"

        safe_url = html.escape(r.url)
        safe_title = html.escape(r.title or "-")
        safe_redirect = html.escape(r.redirect_url or "-")
        size_str = f"{r.content_length:,} B"
        time_str = f"{r.response_time * 1000:.1f} ms"

        row = f"""
        <tr>
            <td class="text-muted">{idx}</td>
            <td><span class="badge {badge_cls}">{r.status_code}</span></td>
            <td><span class="category-tag">{html.escape(r.category.upper())}</span></td>
            <td><a href="{safe_url}" target="_blank" class="url-link">{safe_url}</a></td>
            <td class="text-right mono">{size_str}</td>
            <td class="text-right mono">{time_str}</td>
            <td class="text-muted">{safe_redirect}</td>
            <td class="text-dim">{safe_title}</td>
        </tr>
        """
        rows_html.append(row)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PathHawk Discovery Report - {html.escape(config.target_url or config.domain or 'Target')}</title>
    <style>
        :root {{
            --bg-primary: #0a0e14;
            --bg-secondary: #10161f;
            --bg-card: #151e2b;
            --border-color: #202e42;
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
            --cyan-accent: #00d8ff;
            --green-accent: #00ff88;
            --yellow-accent: #ffcc00;
            --red-accent: #ff4d4f;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-primary);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.5;
            padding: 2rem 1.5rem;
        }}
        .container {{
            max-width: 1300px;
            margin: 0 auto;
        }}
        header {{
            background: linear-gradient(135deg, #101827 0%, #172554 100%);
            border: 1px solid var(--border-color);
            border-top: 4px solid var(--cyan-accent);
            border-radius: 8px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
        }}
        .brand-title {{
            font-size: 2rem;
            font-weight: 800;
            color: var(--green-accent);
            letter-spacing: 1px;
        }}
        .brand-subtitle {{
            color: var(--cyan-accent);
            font-size: 1rem;
            font-weight: 500;
            margin-top: 0.25rem;
        }}
        .dev-badge {{
            display: inline-block;
            background: rgba(0, 216, 255, 0.1);
            color: var(--cyan-accent);
            border: 1px solid rgba(0, 216, 255, 0.3);
            border-radius: 4px;
            padding: 0.2rem 0.6rem;
            font-size: 0.85rem;
            margin-top: 0.75rem;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 1.25rem;
        }}
        .stat-label {{
            font-size: 0.8rem;
            text-transform: uppercase;
            color: var(--text-secondary);
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        .stat-value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-top: 0.5rem;
        }}
        .stat-value.highlight {{
            color: var(--cyan-accent);
        }}
        .table-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }}
        .table-header {{
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .table-header h2 {{
            font-size: 1.2rem;
            color: var(--text-primary);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}
        th {{
            background: var(--bg-secondary);
            color: var(--text-secondary);
            font-weight: 600;
            text-align: left;
            padding: 0.85rem 1rem;
            border-bottom: 1px solid var(--border-color);
        }}
        td {{
            padding: 0.85rem 1rem;
            border-bottom: 1px solid var(--border-color);
        }}
        tr:hover td {{
            background: rgba(255, 255, 255, 0.02);
        }}
        .mono {{
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        }}
        .text-right {{ text-align: right; }}
        .text-muted {{ color: var(--text-secondary); }}
        .text-dim {{ color: #768390; font-size: 0.85rem; }}
        .url-link {{
            color: var(--cyan-accent);
            text-decoration: none;
            word-break: break-all;
            font-family: monospace;
        }}
        .url-link:hover {{ text-decoration: underline; }}
        .badge {{
            display: inline-block;
            font-weight: 700;
            border-radius: 4px;
            padding: 0.15rem 0.5rem;
            font-size: 0.75rem;
            font-family: monospace;
        }}
        .badge-success {{ background: rgba(0, 255, 136, 0.15); color: var(--green-accent); border: 1px solid var(--green-accent); }}
        .badge-info {{ background: rgba(0, 216, 255, 0.15); color: var(--cyan-accent); border: 1px solid var(--cyan-accent); }}
        .badge-warning {{ background: rgba(255, 204, 0, 0.15); color: var(--yellow-accent); border: 1px solid var(--yellow-accent); }}
        .badge-danger {{ background: rgba(255, 77, 79, 0.15); color: var(--red-accent); border: 1px solid var(--red-accent); }}
        .category-tag {{
            background: #212c3d;
            color: #94a3b8;
            font-size: 0.7rem;
            font-weight: 600;
            padding: 0.15rem 0.45rem;
            border-radius: 3px;
        }}
        footer {{
            margin-top: 3rem;
            text-align: center;
            font-size: 0.85rem;
            color: var(--text-secondary);
            border-top: 1px solid var(--border-color);
            padding-top: 1.5rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand-title">{__title__} v{__version__}</div>
            <div class="brand-subtitle">{__tagline__} • Web Asset Discovery Report</div>
            <div class="dev-badge">Developed by {__author__} | {__organization__}</div>
            <p style="margin-top: 0.75rem; font-size: 0.85rem; color: #94a3b8;">
                Target: <strong>{html.escape(config.target_url or config.domain or 'Unknown')}</strong> | 
                Generated on: <strong>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</strong>
            </p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Findings</div>
                <div class="stat-value highlight">{len(results)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Status 200 OK</div>
                <div class="stat-value" style="color: var(--green-accent);">{status_counts.get(200, 0)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Redirects (30x)</div>
                <div class="stat-value" style="color: var(--cyan-accent);">{sum(status_counts.get(c, 0) for c in (301, 302, 307, 308))}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Protected (401/403)</div>
                <div class="stat-value" style="color: var(--yellow-accent);">{status_counts.get(401, 0) + status_counts.get(403, 0)}</div>
            </div>
        </div>

        <div class="table-card">
            <div class="table-header">
                <h2>Discovered Endpoints & Records</h2>
                <span class="text-muted">{len(results)} items found</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 40px;">#</th>
                        <th style="width: 80px;">Status</th>
                        <th style="width: 90px;">Category</th>
                        <th>Discovered Asset</th>
                        <th class="text-right" style="width: 110px;">Size</th>
                        <th class="text-right" style="width: 100px;">Latency</th>
                        <th>Redirect / Details</th>
                        <th>Page Title</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows_html) if rows_html else '<tr><td colspan="8" style="text-align:center; padding: 2rem;">No endpoints matched current filters.</td></tr>'}
                </tbody>
            </table>
        </div>

        <footer>
            <p>Generated by <strong>{__title__}</strong> — Developed and maintained by <strong>{__author__}</strong> ({__organization__}).</p>
            <p style="margin-top: 0.3rem;">Notice: This report is generated strictly for authorized security assessments.</p>
        </footer>
    </div>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_path
