import requests, json, os, re
from rich.console import Console

console = Console()

GRAPHQL_INTROSPECTION = '''
{
  __schema {
    queryType { name }
    mutationType { name }
    types {
      name kind
      fields(includeDeprecated: true) {
        name
        args { name type { name kind ofType { name kind } } }
        type { name kind ofType { name kind } }
      }
    }
  }
}
'''

SWAGGER_PATHS = [
    '/swagger.json', '/openapi.json', '/api-docs',
    '/api/swagger.json', '/api/openapi.json',
    '/v1/swagger.json', '/v2/swagger.json', '/v3/swagger.json',
    '/swagger/v1/swagger.json', '/swagger-ui.html',
    '/api/docs', '/docs/api', '/redoc',
]

GRAPHQL_PATHS = [
    '/graphql', '/api/graphql', '/graphql/v1',
    '/graphiql', '/playground', '/api/v1/graphql',
    '/v1/graphql', '/v2/graphql',
]


def probe_graphql(base_url, headers=None):
    headers = headers or {'Content-Type': 'application/json'}
    results = []

    for path in GRAPHQL_PATHS:
        url = base_url.rstrip('/') + path
        try:
            r = requests.post(
                url,
                json={'query': GRAPHQL_INTROSPECTION},
                headers=headers,
                timeout=10
            )
            if r.status_code == 200 and '__schema' in r.text:
                data = r.json()
                schema = data.get('data', {}).get('__schema', {})
                types = schema.get('types', [])

                # Filter out built-in types
                custom_types = [
                    t for t in types
                    if t.get('name') and not t['name'].startswith('__')
                ]

                query_type = schema.get('queryType', {}).get('name', 'Query')
                mutation_type = schema.get('mutationType', {})
                mutation_name = mutation_type.get('name') if mutation_type else None

                queries = []
                mutations = []
                for t in custom_types:
                    if t.get('name') == query_type:
                        queries = t.get('fields') or []
                    elif mutation_name and t.get('name') == mutation_name:
                        mutations = t.get('fields') or []

                results.append({
                    'url': url,
                    'type': 'graphql',
                    'introspection': 'enabled',
                    'query_count': len(queries),
                    'mutation_count': len(mutations),
                    'queries': [q['name'] for q in queries],
                    'mutations': [m['name'] for m in mutations],
                    'custom_types': [t['name'] for t in custom_types],
                })

                console.print(
                    f'[bold red][!!!][/bold red] GraphQL introspection ENABLED: [cyan]{url}[/cyan]'
                )
                console.print(
                    f'    Queries: {len(queries)} | Mutations: {len(mutations)}'
                )

        except Exception:
            continue

    return results


def probe_swagger(base_url):
    results = []

    for path in SWAGGER_PATHS:
        url = base_url.rstrip('/') + path
        try:
            r = requests.get(url, timeout=10, allow_redirects=True)
            if r.status_code == 200 and len(r.text) > 100:
                content_type = r.headers.get('Content-Type', '')

                if 'json' in content_type or url.endswith('.json'):
                    try:
                        spec = r.json()
                        paths = spec.get('paths', {})
                        endpoints = []
                        for ep_path, methods in paths.items():
                            for method in methods.keys():
                                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                                    endpoints.append(f'{method.upper()} {ep_path}')

                        results.append({
                            'url': url,
                            'type': 'openapi',
                            'spec_version': spec.get('openapi') or spec.get('swagger', 'unknown'),
                            'endpoint_count': len(endpoints),
                            'endpoints': endpoints,
                        })

                        console.print(
                            f'[bold red][!!!][/bold red] OpenAPI spec found: [cyan]{url}[/cyan]'
                        )
                        console.print(f'    Endpoints mapped: {len(endpoints)}')

                    except Exception:
                        results.append({
                            'url': url,
                            'type': 'swagger-ui',
                            'note': 'HTML UI found — manual review needed',
                        })
                        console.print(f'[yellow][*][/yellow] Swagger UI found: {url}')

        except Exception:
            continue

    return results


def map_api(out):
    console.rule('[bold cyan]Phase 4.5 - API Schema Mapper[/bold cyan]')

    hosts_file = f'{out}/live_hosts.txt'
    if not os.path.exists(hosts_file):
        console.print('[yellow][!] No live_hosts.txt found — skipping API mapper[/yellow]')
        return

    with open(hosts_file) as f:
        hosts = [h.strip() for h in f if h.strip()]

    if not hosts:
        console.print('[yellow][!] No live hosts to probe[/yellow]')
        return

    console.print(f'[cyan][*][/cyan] Probing {len(hosts)} hosts for API schemas...')

    all_findings = []

    for host in hosts:
        base = host if host.startswith('http') else f'https://{host}'

        graphql_results = probe_graphql(base)
        swagger_results = probe_swagger(base)

        all_findings.extend(graphql_results)
        all_findings.extend(swagger_results)

    # Write JSON output
    json_out = f'{out}/api_surface.json'
    with open(json_out, 'w') as f:
        json.dump(all_findings, f, indent=2)

    # Write Markdown output
    md_out = f'{out}/api_surface.md'
    with open(md_out, 'w') as f:
        f.write('# API Surface Map\n\n')
        if not all_findings:
            f.write('No API schemas discovered.\n')
        else:
            for item in all_findings:
                f.write(f"## {item['url']}\n")
                f.write(f"- **Type:** {item['type']}\n")
                if item['type'] == 'graphql':
                    f.write(f"- **Queries:** {item['query_count']}\n")
                    f.write(f"- **Mutations:** {item['mutation_count']}\n")
                    if item['queries']:
                        f.write(f"- **Query list:** {', '.join(item['queries'])}\n")
                    if item['mutations']:
                        f.write(f"- **Mutation list:** {', '.join(item['mutations'])}\n")
                elif item['type'] == 'openapi':
                    f.write(f"- **Spec version:** {item.get('spec_version', 'unknown')}\n")
                    f.write(f"- **Endpoints:** {item.get('endpoint_count', 0)}\n")
                    for ep in item.get('endpoints', []):
                        f.write(f"  - `{ep}`\n")
                f.write('\n')

    if all_findings:
        console.print(
            f'[bold red][!!!][/bold red] API endpoints mapped: '
            f'{len(all_findings)} -> {json_out}'
        )
    else:
        console.print('[green][+][/green] No API schemas found')
