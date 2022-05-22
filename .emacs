
;; Added by Package.el.  This must come before configurations of
;; installed packages.  Don't delete this line.  If you don't want it,
;; just comment it out by adding a semicolon to the start of the line.
;; You may delete these explanatory comments.
(package-initialize)

(require 'package)
(add-to-list 'package-archives
             '("melpa" . "http://melpa.org/packages/") t)

(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(custom-safe-themes
   (quote
    ("51ec7bfa54adf5fff5d466248ea6431097f5a18224788d0bd7eb1257a4f7b773" "efcecf09905ff85a7c80025551c657299a4d18c5fcfedd3b2f2b6287e4edd659" "830877f4aab227556548dc0a28bf395d0abe0e3a0ab95455731c9ea5ab5fe4e1" "833ddce3314a4e28411edf3c6efde468f6f2616fc31e17a62587d6a9255f4633" "fee7287586b17efbfda432f05539b58e86e059e78006ce9237b8732fde991b4c" "4c56af497ddf0e30f65a7232a8ee21b3d62a8c332c6b268c81e9ea99b11da0d3" "57a29645c35ae5ce1660d5987d3da5869b048477a7801ce7ab57bfb25ce12d3e" "eb5c79b2e9a91b0a47b733a110d10774376a949d20b88c31700e9858f0f59da7" "fc48cc3bb3c90f7761adf65858921ba3aedba1b223755b5924398c666e78af8b" "8b8fd1c936a20b5ca6afe22e081798ffb5e7498021515accadc20aab3517d402" "c48551a5fb7b9fc019bf3f61ebf14cf7c9cdca79bcb2a4219195371c02268f11" default)))
 '(package-selected-packages (quote (solarized-theme magit))))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )

(setq inhibit-startup-screen t)
(tool-bar-mode -1)

;; custom keyboard shortcuts
(global-set-key (kbd "M-u") 'previous-buffer)
(global-set-key (kbd "M-o") 'next-buffer)
(global-set-key (kbd "M-i") 'previous-line)
(global-set-key (kbd "M-k") 'next-line)

(global-set-key (kbd "M-q") 'magit-status)
(global-set-key (kbd "M-l") 'magit-log-all-branches)
(global-set-key (kbd "M-d") 'magit-diff-dwim)

(require 'magit)
(kill-buffer)
(magit-status)
(switch-to-buffer-other-window "*Messages*")
(kill-buffer)

;; theming
(load-theme 'solarized-dark t)

