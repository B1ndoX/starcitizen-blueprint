FROM caddy:2-alpine

COPY Caddyfile /etc/caddy/Caddyfile
COPY index.html /srv/index.html
COPY fleet-command.html /srv/fleet-command.html
COPY site.webmanifest /srv/site.webmanifest
COPY assets /srv/assets
COPY data /srv/data
