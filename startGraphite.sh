docker run -d \
 --name graphite2 \
 --restart=always \
 -p 80:80 \
 -p 2003-2004:2003-2004 \
 -p 2023-2024:2023-2024 \
 -p 8125:8125/udp \
 -p 2003:2003/udp \
 -p 8126:8126 \
 graphiteapp/graphite-statsd2
