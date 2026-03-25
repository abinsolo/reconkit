import os, datetime
from rich.console import Console
from rich.table import Table

console = Console()

# Tier definitions — no monetary values
TRIAGE_TIERS = {
    'CRITICAL': {
        'color': 'bold red',
        'priority': 1,
        'action': 'Report immediately — high priority',
    },
    'HIGH': {
        'color': 'red',
        'priority': 2,
        'action': 'Verify and report same day',
    },
    'MEDIUM': {
        'color': 'yellow',
        'priority': 3,
        'action': 'Verify impact before reporting',
    },
    'LOW': {
        'color': 'cyan',
        'priority': 4,
        'action': 'Batch report or skip',
    },
    'INFO': {
        'color': 'white',
        'priority': 5,
        'action': 'Review manually — likely not reportable',
    },
}

# Keywords that map to each tier
TIER_KEYWORDS = {
    'CRITICAL': [
        'rce', 'remote-code-execution', 'sql-injection', 'sqli',
        'auth-bypass', 'authentication-bypass', 'ssrf',
        'xxe', 'xml-external-entity', 'deserialization',
        'command-injection', 'code-injection',
    ],
    'HIGH': [
        'default-login', 'default-credentials', 'exposed-panel',
        'admin-panel', 'exposed-admin', 'cve',
        'open-redirect', 'idor', 'privilege-escalation',
        'jwt', 'broken-auth',
    ],
    'MEDIUM': [
        'misconfig', 'misconfiguration', 'exposed-api',
        'takeover', 'subdomain-takeover', 'cors',
        'xss', 'cross-site-scripting', 'csrf',
        'path-traversal', 'lfi', 'rfi',
        'api-key', 'secret', 'token',
    ],
    'LOW': [
        'info-disclosure', 'information-disclosure',
        'missing-header', 'security-header',
        'outdated-software', 'version-disclosure',
        'directory-listing', 'debug-enabled',
    ],
    'INFO': [
        'tech-detect', 'fingerprint', 'robots-txt',
        'sitemap', 'email', 'dns',
        'ssl', 'tls', 'certificate',
    ],
}


def classify(line):
    """Classify a nuclei finding line into a triage tier."""
    line_lower = line.lower()

    for tier in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
        for keyword in TIER_KEYWORDS[tier]:
            if keyword in line_lower:
                return tier

    # Fallback: check for severity tags in nuclei output format
    if '[critical]' in line_lower:
        return 'CRITICAL'
    elif '[high]' in line_lower:
        return 'HIGH'
    elif '[medium]' in line_lower:
        return 'MEDIUM'
    elif '[low]' in line_lower:
        return 'LOW'

    return 'INFO'


def detect_platform(out):
    if os.path.exists(f'{out}/scope_hackerone.txt') and \
       not os.path.exists(f'{out}/scope_intigriti.txt'):
        return 'HackerOne'
    elif os.path.exists(f'{out}/scope_intigriti.txt') and \
         not os.path.exists(f'{out}/scope_hackerone.txt'):
        return 'Intigriti'
    return 'HackerOne + Intigriti'


def triage(out):
    console.rule('[bold cyan]Phase 5.5 - Bounty Triage Layer[/bold cyan]')

    platform = detect_platform(out)

    findings_file = f'{out}/nuclei_findings.txt'
    if not os.path.exists(findings_file):
        # Also try nuclei_output.txt as fallback
        findings_file = f'{out}/nuclei_output.txt'
        if not os.path.exists(findings_file):
            console.log('[yellow][!] No nuclei findings file found — skipping triage[/yellow]')
            return

    lines = [l.strip() for l in open(findings_file).readlines() if l.strip()]

    if not lines:
        console.log('[green][+][/green] No findings to triage')
        return

    # Sort findings into buckets
    buckets = {
        'CRITICAL': [],
        'HIGH':     [],
        'MEDIUM':   [],
        'LOW':      [],
        'INFO':     [],
    }

    for line in lines:
        tier = classify(line)
        buckets[tier].append(line)

    # Print rich summary table
    table = Table(title='Triage Report', style='bold')
    table.add_column('Tier',     style='bold', width=10)
    table.add_column('Count',    width=7)
    table.add_column('Platform', width=20)
    table.add_column('Action',   width=40)

    for tier, info in TRIAGE_TIERS.items():
        count = len(buckets[tier])
        if count > 0:
            table.add_row(
                f"[{info['color']}]{tier}[/{info['color']}]",
                str(count),
                platform,
                info['action'],
            )

    console.print(table)

    # Write TRIAGE_REPORT.md
    report_path = f'{out}/TRIAGE_REPORT.md'
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(report_path, 'w') as f:
        f.write('# Triage Report\n\n')
        f.write(f'**Date:** {date}\n\n')
        f.write(f'**Platform:** {platform}\n\n')

        f.write('## Summary\n\n')
        f.write('| Tier | Count | Platform | Action |\n')
        f.write('|------|-------|----------|--------|\n')

        for tier, info in TRIAGE_TIERS.items():
            count = len(buckets[tier])
            if count > 0:
                f.write(f'| {tier} | {count} | {platform} | {info["action"]} |\n')

        f.write('\n\n## Findings by Tier\n\n')

        for tier in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            if buckets[tier]:
                f.write(f'### {tier}\n\n')
                for finding in buckets[tier]:
                    f.write(f'- {finding}\n')
                f.write('\n')

    console.log(f'[green][+][/green] Triage report -> {report_path}')

    # Return highest tier found
    for tier in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
        if buckets[tier]:
            return tier

    return 'INFO'
