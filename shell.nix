{ pkgs? import <nixpkgs> {}, ... }:
with pkgs;

let
  my-pkgs = import /home/diego/prog/nixpkgs {
    config.allowUnfree = true;
  };

  customPython = pkgs.python38.buildEnv.override {
    extraLibs = with pkgs.python38Packages; [
      setuptools
      pip
      click
      fastapi
    ];
  };
in
mkShell {
  buildInputs = [
    # customPython
    my-pkgs.nodejs
    my-pkgs.nodePackages.npm
  ];

  shellHook = ''
    export PATH="$PATH:$HOME/prog/book/node_modules/.bin"
  '';
}
