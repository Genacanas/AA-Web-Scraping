import pandas as pd
import numpy as np

# Ruta del archivo de entrada y salida
input_file = "auto_parts_final_modif.xlsx"
output_file = "auto_parts_final_modified.xlsx"

# Cargar el archivo Excel
df = pd.read_excel(input_file)

# Función para reemplazar el valor de "Heading SKU" si aparece en "Hardware Number[s]"
def remove_if_match(row):
    sku = str(row['Heading SKU']).strip()
    hw_nums = str(row['Hardware Number[s]']).strip()
    if sku and sku in hw_nums:
        return np.nan  # o "" si prefieres cadena vacía
    return row['Heading SKU']

# Aplicar la función fila por fila
df['Heading SKU'] = df.apply(remove_if_match, axis=1)

# Guardar el archivo modificado
df.to_excel(output_file, index=False)

print(f"Archivo modificado guardado como '{output_file}'")
