import pandas as pd

def save_to_excel(df, path):
    df.to_excel(path, index=False)
    print(f'Saved results to {path}')
