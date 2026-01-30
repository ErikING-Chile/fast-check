
import os
import sys
import glob

def apply_patch(file_path, target, replacement, description):
    if not os.path.exists(file_path):
        print(f"Skipping {description}: File not found {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if replacement in content:
        print(f"Skipping {description}: Already patched")
        return True
    
    if target not in content:
        print(f"Skipping {description}: Target content not found (version mismatch?)")
        return False
        
    new_content = content.replace(target, replacement)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Applied patch: {description}")
        return True
    except Exception as e:
        print(f"Failed to patch {description}: {e}")
        return False

def patch_dependencies():
    print("Checking dependencies patches...")
    
    # Locate site-packages by finding a known package
    import speechbrain
    sb_path = os.path.dirname(speechbrain.__file__)
    site_packages = os.path.dirname(sb_path)
    
    # 1. Patch pyannote.audio mixins (AudioMetaData)
    mixins_path = os.path.join(site_packages, "pyannote", "audio", "tasks", "segmentation", "mixins.py")
    apply_patch(
        mixins_path,
        "from torchaudio.backend.common import AudioMetaData",
        """try:
    from torchaudio import AudioMetaData
except ImportError:
    try:
        from torchaudio.backend.common import AudioMetaData
    except ImportError:
        from collections import namedtuple
        AudioMetaData = namedtuple("AudioMetaData", ["sample_rate", "num_frames", "num_channels", "bits_per_sample", "encoding"])""",
        "pyannote AudioMetaData fix"
    )

    # 2. Patch lightning fabric (weights_only default)
    cloud_io_path = os.path.join(site_packages, "lightning_fabric", "utilities", "cloud_io.py")
    apply_patch(
        cloud_io_path,
        '    """\n    if not isinstance(path_or_url, (str, Path)):',
        '    """\n    if weights_only is None:\n        weights_only = False\n    if not isinstance(path_or_url, (str, Path)):',
        "lightning weights_only default fix"
    )
    
    # 3. Patch speechbrain fetching (use_auth_token deprecated)
    fetching_path = os.path.join(site_packages, "speechbrain", "utils", "fetching.py")
    apply_patch(
        fetching_path,
        '"use_auth_token": use_auth_token,',
        '"token": use_auth_token,',
        "speechbrain use_auth_token fix"
    )

    # 4. Patch pyannote pipeline (use_auth_token -> token)
    pipeline_path = os.path.join(site_packages, "pyannote", "audio", "core", "pipeline.py")
    apply_patch(
        pipeline_path,
        "use_auth_token=use_auth_token",
        "token=use_auth_token",
        "pyannote pipeline use_auth_token fix"
    )

    # 5. Patch pyannote model (use_auth_token -> token) - multiple occurrences
    model_path = os.path.join(site_packages, "pyannote", "audio", "core", "model.py")
    # This might need a regex or loop if multiple replaces are strictly identical strings
    # We'll just replace the string globally as it's safe here
    apply_patch(
        model_path,
        "use_auth_token=use_auth_token",
        "token=use_auth_token",
        "pyannote model use_auth_token fix"
    )

if __name__ == "__main__":
    patch_dependencies()
