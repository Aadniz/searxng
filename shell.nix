{ pkgs ? import <nixpkgs> {} }:

/* $ nix-shell
 * $ make run
 */

pkgs.mkShell {
  packages = with pkgs; [
    bashInteractive
    wget
    gnumake
    git
    python3
    geckodriver
    shellcheck
  ];
}
