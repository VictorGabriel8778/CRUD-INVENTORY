import time

agora = time.localtime()

data_hoje = f"{agora.tm_mday:02d}/{agora.tm_mon:02d}/{agora.tm_year}"
print(data_hoje)