# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/static', 'app/static'),  # 静态文件目录
        ('favicon.ico', '.'),          # 图标文件
        ('config.py', '.'),            # 配置文件
        ('files', 'files'),            # 数据文件目录
        ('.env.production', '.'),      # 生产环境配置文件
    ],
    hiddenimports=[
        'flask',
        'numpy', 
        'numpy.core',
        'numpy.core._multiarray_umath',
        'numpy.core._multiarray_tests',
        'numpy.linalg._umath_linalg',
        'numpy.random._common',
        'numpy.random.bit_generator',
        'numpy.random._bounded_integers',
        'numpy.random._mt19937',
        'numpy.random.mtrand',
        'numpy.random._philox',
        'numpy.random._pcg64',
        'numpy.random._sfc64',
        'cv2',
        'cv2.cv2',
        'win32gui',
        'win32ui',
        'win32con',
        'win32api',
        'win32process',
        'psutil',
        'sqlite3',
        'threading',
        'logging',
        'argparse',
        'dataclasses',
        'contextlib',
        'subprocess',
        'app',
        'app.api',
        'app.api.controllers',
        'app.api.views',
        'app.domain',
        'app.domain.entities',
        'app.infrastructure',
        'app.infrastructure.database',
        'app.infrastructure.manager',
        'app.infrastructure.utils',
    ],
    hookspath=[],
    hooksconfig={
        'cv2': {
            'module_collection_mode': 'pyz+py',
        },
    },
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'tkinter',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Canliang_',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='favicon.ico',
)
