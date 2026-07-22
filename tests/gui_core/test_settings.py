import colorsortgui.settings as st

def test_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(st, "settings_dir", lambda: tmp_path)
    st.save_settings({"lang": "ko", "gamma": 0.35})
    assert st.load_settings()["lang"] == "ko"
    assert (tmp_path / "colorsort-settings.json").exists()

def test_missing_file_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(st, "settings_dir", lambda: tmp_path)
    assert st.load_settings() == {}

def test_corrupt_file_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(st, "settings_dir", lambda: tmp_path)
    (tmp_path / "colorsort-settings.json").write_text("{bad", encoding="utf-8")
    assert st.load_settings() == {}

def test_unwritable_falls_back(tmp_path, monkeypatch):
    ro = tmp_path / "ro"; ro.mkdir()
    appdata = tmp_path / "appdata"
    monkeypatch.setenv("APPDATA", str(appdata))
    monkeypatch.setattr(st, "_primary_dir", lambda: ro)
    monkeypatch.setattr(st, "_dir_writable", lambda p: p != ro)
    assert st.settings_dir() == appdata / "Colorsort"
