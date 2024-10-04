{ pkgs, ... }: {
  channel = "stable-23.11";

  packages = with pkgs; [
    python311Full
    python311Packages.pip
    python311Packages.virtualenv
    libGL
    libGLU
    xorg.libX11
    xorg.libXext
    xorg.libXrender
    xorg.libICE
    xorg.libSM
  ];

  env = {
    PYTHONPATH = "${pkgs.python311Full}/bin:${pkgs.python311Packages.pip}/bin:$PYTHONPATH";
    LD_LIBRARY_PATH = with pkgs; lib.makeLibraryPath [
      libGL
      libGLU
      xorg.libX11
      xorg.libXext
      xorg.libXrender
      xorg.libICE
      xorg.libSM
    ];
    OPENAI_API_KEY = "$OPENAI_API_KEY";  # Use environment variable
  };

  idx = {
    extensions = [
      "ms-python.python"
    ];
    workspace = {
      onCreate = [
        "python -m ensurepip --upgrade"
        "python -m venv myenv --system-site-packages"
        "source myenv/bin/activate"
        "python -m pip install --upgrade pip"
        "pip install -r requirements.txt"
        "if [ -f .env ]; then set -a; source .env; set +a; fi"
      ];
      onStart = [
        "source myenv/bin/activate"
        "if [ -f .env ]; then set -a; source .env; set +a; fi"
      ];
    };
  };
}
