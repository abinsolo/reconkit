import os, requests
from rich.console import Console

console = Console()

# Your API credentials
H1_USERNAME   = 'abinsolo'
H1_API_TOKEN  = 'v1sw77dbFBGVHM4Wzdx7HVHSkgMCdI16PTl1DQT+mog='
INTIGRITI_TOKEN = '071E7065C1F524365E2288E5D967A2B11015BC49B2E16DDD94C5E1162DE07A20-1'


def fetch_hackerone(program_handle, out):
    """Fetch in-scope domains from HackerOne API."""
    url = f'https://api.hackerone.com/v1/hackers/programs/{program_handle}'
    headers = {'Accept': 'application/json'}

    try:
        req_kwargs = dict(headers=headers, timeout=10)
        if H1_USERNAME and H1_API_TOKEN:
            req_kwargs['auth'] = ('abinsolo','v1sw77dbFBGVHM4Wzdx7HVHSkgMCdI16PTl1DQT+mog=')
        else:
            console.log('[yellow][*] No H1 credentials set — set H1_USERNAME and H1_API_TOKEN in scope_engine.py[/yellow]')
            return None

        r = requests.get(url, **req_kwargs)

        if r.status_code == 401:
            console.log('[red][!] HackerOne API returned 401 — check your API token[/red]')
            return None
        if r.status_code == 404:
            console.log(f'[red][!] HackerOne program not found: {program_handle}[/red]')
            console.log('[yellow][*] Check the exact program handle on hackerone.com[/yellow]')
            return None
        if r.status_code != 200:
            console.log(f'[red][!] HackerOne API returned {r.status_code}[/red]')
            return None

        data = r.json()
        scope_domains = []

        targets = (
            data.get('relationships', {})
                .get('structured_scopes', {})
                .get('data', [])
        )

        for target in targets:
            attrs = target.get('attributes', {})
            asset_type = attrs.get('asset_type', '')
            eligible   = attrs.get('eligible_for_bounty', False)

            if asset_type == 'URL' and eligible:
                identifier = attrs.get('asset_identifier', '')
                identifier = identifier.replace('https://', '').replace('http://', '')
                identifier = identifier.replace('*', '').strip().strip('/')
                if identifier:
                    scope_domains.append(identifier)

        if not scope_domains:
            console.log('[yellow][*] No bounty-eligible URL scope found on HackerOne[/yellow]')
            return None

        scope_file = f'{out}/scope_hackerone.txt'
        with open(scope_file, 'w') as f:
            f.write('\n'.join(scope_domains))

        console.log(
            f'[green][+][/green] HackerOne scope: {len(scope_domains)} domains -> {scope_file}'
        )
        return scope_file

    except Exception as e:
        console.log(f'[red][!] HackerOne fetch failed: {e}[/red]')
        return None


def fetch_intigriti(program_handle, out):
    """Fetch in-scope domains from Intigriti API."""
    url = f'https://api.intigriti.com/core/researcher/program/{program_handle}'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {INTIGRITI_TOKEN}',
    }

    try:
        if not INTIGRITI_TOKEN:
            console.log('[yellow][*] No Intigriti token set — set INTIGRITI_TOKEN in scope_engine.py[/yellow]')
            return None

        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code == 401:
            console.log('[red][!] Intigriti API returned 401 — check your Bearer token[/red]')
            return None
        if r.status_code == 404:
            console.log(f'[red][!] Intigriti program not found: {program_handle}[/red]')
            console.log('[yellow][*] Find the exact slug in the Intigriti program URL:[/yellow]')
            console.log('[yellow][*] app.intigriti.com/programs/COMPANY/SLUG/detail[/yellow]')
            return None
        if r.status_code != 200:
            console.log(f'[red][!] Intigriti API returned {r.status_code}[/red]')
            return None

        data = r.json()
        scope_domains = []

        domains = data.get('domains', {}).get('inScope', [])
        for d in domains:
            endpoint = d.get('endpoint', '')
            endpoint = endpoint.replace('https://', '').replace('http://', '')
            endpoint = endpoint.replace('*', '').strip().strip('/')
            if endpoint and '.' in endpoint:
                scope_domains.append(endpoint)

        if not scope_domains:
            console.log('[yellow][*] No in-scope domains found on Intigriti[/yellow]')
            return None

        scope_file = f'{out}/scope_intigriti.txt'
        with open(scope_file, 'w') as f:
            f.write('\n'.join(scope_domains))

        console.log(
            f'[green][+][/green] Intigriti scope: {len(scope_domains)} domains -> {scope_file}'
        )
        return scope_file

    except Exception as e:
        console.log(f'[red][!] Intigriti fetch failed: {e}[/red]')
        return None


def auto_scope(platform, program_handle, out):
    """Main entry. Returns path to scope file or None."""
    console.rule('[bold yellow]Auto-Scope Fetch[/bold yellow]')
    os.makedirs(out, exist_ok=True)

    if platform.lower() == 'hackerone':
        return fetch_hackerone(program_handle, out)
    elif platform.lower() == 'intigriti':
        return fetch_intigriti(program_handle, out)
    else:
        console.log(
            f'[red][!] Unknown platform: {platform}. Use hackerone or intigriti[/red]'
        )
        return None

