export const APP_VERSION: string = process.env.NEXT_PUBLIC_APP_VERSION ?? '0.0.0';

function normalize(v: string): string {
  return (v || '').trim().replace(/^v/i, '');
}

export function compareVersions(a: string, b: string): number {
  const pa = normalize(a).split('.');
  const pb = normalize(b).split('.');
  const len = Math.max(pa.length, pb.length);
  for (let i = 0; i < len; i++) {
    const na = parseInt(pa[i] ?? '0', 10);
    const nb = parseInt(pb[i] ?? '0', 10);
    if (Number.isNaN(na) || Number.isNaN(nb)) {
      // If non-numeric segments exist, fallback to string compare
      const sa = pa[i] ?? '';
      const sb = pb[i] ?? '';
      if (sa > sb) return 1;
      if (sa < sb) return -1;
      continue;
    }
    if (na > nb) return 1;
    if (na < nb) return -1;
  }
  return 0;
}

export function isNewerVersion(latest: string, current: string): boolean {
  return compareVersions(latest, current) > 0;
}

async function fetchJson(url: string, headers?: Record<string, string>) {
  const res = await fetch(url, {
    headers: headers ?? {},
    cache: 'no-store',
  });
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function fetchLatestGithubRelease(
  owner: string = 'Because66666',
  repo: string = 'CanLiang',
  token?: string
): Promise<{ tag: string; publishedAt: string; url: string }> {
  const headers: Record<string, string> = {
    Accept: 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  // Try releases/latest first
  try {
    const data = await fetchJson(
      `https://api.github.com/repos/${owner}/${repo}/releases/latest`,
      headers
    );
    const tag = (data.tag_name ?? data.name ?? '').toString();
    return {
      tag,
      publishedAt: data.published_at ?? '',
      url: data.html_url ?? `https://github.com/${owner}/${repo}/releases/latest`,
    };
  } catch (e: any) {
    // Fallback to tags (in case no releases exist)
    try {
      const data = await fetchJson(
        `https://api.github.com/repos/${owner}/${repo}/tags?per_page=1`,
        headers
      );
      const first = Array.isArray(data) ? data[0] : undefined;
      const tag = (first?.name ?? '').toString();
      return {
        tag,
        publishedAt: '',
        url: `https://github.com/${owner}/${repo}/tags`,
      };
    } catch (e2) {
      throw e; // propagate original error
    }
  }
}

export async function checkForUpdate(
  owner: string,
  repo: string,
  token?: string
): Promise<{ current: string; latest: string; hasUpdate: boolean; url: string }> {
  const current = normalize(APP_VERSION);
  const { tag, url } = await fetchLatestGithubRelease(owner, repo, token);
  const latest = normalize(tag);
  console.log('current',current,'latest',latest)
  return {
    current,
    latest,
    hasUpdate: isNewerVersion(latest, current),
    url,
  };
}

export function getCurrentVersion(): string {
  return normalize(APP_VERSION);
}