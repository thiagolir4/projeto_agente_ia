import duckdb

# Conectar ao banco
conn = duckdb.connect("./data/finance.duckdb")

# Exportar tabela datasets
conn.execute("COPY datasets TO 'data/datasets_export.csv' (HEADER, DELIMITER ',')")

# Listar tabelas
tables = conn.execute("SHOW TABLES").fetchall()
print("Tabelas disponíveis:", tables)

conn.close()
