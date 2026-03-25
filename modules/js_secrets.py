import re, os, json, requests
from rich.console import Console
console = Console()

# Secret patterns — (name, regex)
SECRET_PATTERNS = [
    ('AWS Access Key',    r'AKIA[0-9A-Z]{16}'),
    ('AWS Secret Key',    r'(?i)aws.{0,20}secret.{0,20}[\'"][0-9a-zA-Z/+]{40}[\'"]'),
    ('Google API Key',    r'AIza[0-9A-Za-z\-_]{35}'),
    ('Firebase URL',      r'https://[a-z0-9-]+\.firebaseio\.com'),
    ('Stripe Secret Key', r'sk_live_[0-9a-zA-Z]{24}'),
    ('Stripe Pub Key',    r'pk_live_[0-9a-zA-Z]{24}'),
    ('GitHub Token',      r'ghp_[0-9a-zA-Z]{36}'),
    ('GitHub OAuth',      r'gho_[0-9a-zA-Z]{36}'),
    ('Slack Token',       r'xox[baprs]-[0-9a-zA-Z]{10,48}'),
    ('Slack Webhook',     r'https://hooks\.slack\.com/services/[A-Z0-9/]+'),
    ('JWT Token',         r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}'),
    ('Private Key',       r'-----BEGIN (RSA |EC )?PRIVATE KEY-----'),
    ('Bearer Token',      r'(?i)bearer\s+[a-zA-Z0-9\-_\.]{20,}'),
    ('Basic Auth',        r'(?i)basic\s+[a-zA-Z0-9+/=]{20,}'),
    ('Twilio Key',        r'SK[0-9a-fA-F]{32}'),
    ('SendGrid Key',      r'SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}'),
    ('Mailgun Key',       r'key-[0-9a-zA-Z]{32}'),
    ('HerokuAPIKey',      r'(?i)heroku.{0,20}[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}'),
    ('Generic API Key',   r'(?i)(api_key|apikey|api-key)[\s]*[=:][\s]*[\'"][a-zA-Z0-9_\-]{16,}[\'"]'),
    ('Generic Secret',    r'(?i)(secret|password|passwd|pwd)[\s]*[=:][\s]*[\'"][a-zA-Z0-9_\-@!]{8,}[\'"]'),
    ('Generic Token',     r'(?i)(token|access_token|auth_token)[\s]*[=:][\s]*[\'"][a-zA-Z0-9_\-\.]{16,}[\'"]'),
    ('MongoDB URI',       r'mongodb(\+srv)?://[^\s]+'),
    ('MySQL URI',         r'mysql://[^\s]+'),
    ('Postgres URI',      r'postgres(ql)?://[^\s]+'),
    ('S3 Bucket URL',     r'https?://[a-z0-9\-\.]+\.s3\.amazonaws\.com'),
]

def mask(value, show=6):
    if len(value) <= show * 2:
        return value[:show] + '***'
    return value[:show] + '***' + value[-4:]

def scan_js_content(content, url):
    findings = []
    lines = content.split('\n')
    for pattern_name, pattern in SECRET_PATTERNS:
        try:
            for i, line in enumerate(lines):
                matches = re.findall(pattern, line)
                for match in matches:
                    findings.append({
                        'type':  pattern_name,
                        'url':   url,
                        'line':  i + 1,
                        'value': mask(match),
                        'raw':   match,
                    })
        except Exception:
            continue
    return findings

def fetch_js(url, timeout=10):
    try:
        r = requests.get(url, timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return None

def hunt(out):
    console.rule('[bold yellow]Phase 3.5 - JS Secret Hunter')
    all_urls_file = f'{out}/all_urls.txt'
    if not os.path.exists(all_urls_file):
        console.log('[red][!] all_urls.txt not found — run Phase 3 first[/red]')
        return 0

    # Extract .js URLs
    js_urls = []
    with open(all_urls_file) as f:
        for line in f:
            url = line.strip()
            if url.endswith('.js') or '.js?' in url:
                js_urls.append(url)
    js_urls = list(set(js_urls))
    console.log(f'[cyan][*] JS files to scan: {len(js_urls)}[/cyan]')

    if not js_urls:
        console.log('[yellow][*] No JS files found — skipping[/yellow]')
        return 0

    all_findings = []
    for i, url in enumerate(js_urls):
        content = fetch_js(url)
        if not content:
            continue
        findings = scan_js_content(content, url)
        if findings:
            all_findings.extend(findings)
            console.log(f'[red][!!!] {len(findings)} secrets in: {url}[/red]')
        if i % 10 == 0 and i > 0:
            console.log(f'[cyan][*] Scanned {i}/{len(js_urls)} JS files...[/cyan]')

    # Write results
    txt_path  = f'{out}/js_secrets.txt'
    json_path = f'{out}/js_secrets.json'
    with open(json_path, 'w') as f:
        json.dump(all_findings, f, indent=2)
    with open(txt_path, 'w') as f:
        for finding in all_findings:
            f.write(
                f"[{finding['type']}] "
                f"{finding['url']} "
                f"line:{finding['line']} "
                f"value:{finding['value']}\n"
            )

    count = len(all_findings)
    if count > 0:
        console.log(f'[bold red][!!!] SECRETS FOUND: {count} -> {json_path}[/bold red]')
    else:
        console.log('[green][+][/green] No secrets found in JS files')
    return count
