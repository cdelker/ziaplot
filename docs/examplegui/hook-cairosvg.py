from PyInstaller.utils.hooks import collect_data_files

collected_data = collect_data_files('cairocffi')
datas = []
for item_path, dest in collected_data:
    datas.append((item_path, 'cairocffi'))
