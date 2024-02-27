{ pkgs }: {
  deps = [
    pkgs.libxcrypt
    pkgs.sqlite-interactive.bin
    pkgs.sqlite.bin
  ];
}