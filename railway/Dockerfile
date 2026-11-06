# Static site served by Caddy (supports video range requests, gzip, caching)
FROM caddy:2.8.4-alpine
COPY railway/Caddyfile /etc/caddy/Caddyfile
COPY index.html /srv/index.html
COPY assets /srv/assets
COPY fonts /srv/fonts
COPY en /srv/en
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
