```bash
poetry run python src/silvervector/examples/init_ecommerce.py
```


```bash
cd src/silvervector/examples/orchard-core/

docker run --name orchardcms --platform linux/amd64 -p 8080:80 -v orchard-data:/app/App_Data orchardproject/orchardcore-cms-linux:latest

docker run -d -p 3000:3000 \
  -v "$(pwd)/orchard-data:/var/lib/grafana/silvervector_data" \
  -e "GF_INSTALL_PLUGINS=frser-sqlite-datasource" \
  --name=silvervector-grafana grafana/grafana-oss
```

Once Grafana is running at http://localhost:3000:

1. The default admin password is "admin".
2. Navigate to Connections > Data Sources;
3. Search for SQLite;
4. In the Path field, enter the container path: `/var/lib/grafana/silvervector_data/demo_orchard.db`.