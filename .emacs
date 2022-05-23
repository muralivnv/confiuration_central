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
    ("1d89fcf0105dd8778e007239c481643cc5a695f2a029c9f30bd62c9d5df6418d" "47e6f8c23eaea064b89ed1361b5824ee4f9562a8c4a30774ee9ee69f9b9d4f69" "67f0f440afa2e68d9d00219b5a56308761af45832fb60769d2b2fd36e3fead45" "aba75724c5d4d0ec0de949694bce5ce6416c132bb031d4e7ac1c4f2dbdd3d580" "51ec7bfa54adf5fff5d466248ea6431097f5a18224788d0bd7eb1257a4f7b773" "efcecf09905ff85a7c80025551c657299a4d18c5fcfedd3b2f2b6287e4edd659" "830877f4aab227556548dc0a28bf395d0abe0e3a0ab95455731c9ea5ab5fe4e1" "833ddce3314a4e28411edf3c6efde468f6f2616fc31e17a62587d6a9255f4633" "fee7287586b17efbfda432f05539b58e86e059e78006ce9237b8732fde991b4c" "4c56af497ddf0e30f65a7232a8ee21b3d62a8c332c6b268c81e9ea99b11da0d3" "57a29645c35ae5ce1660d5987d3da5869b048477a7801ce7ab57bfb25ce12d3e" "eb5c79b2e9a91b0a47b733a110d10774376a949d20b88c31700e9858f0f59da7" "fc48cc3bb3c90f7761adf65858921ba3aedba1b223755b5924398c666e78af8b" "8b8fd1c936a20b5ca6afe22e081798ffb5e7498021515accadc20aab3517d402" "c48551a5fb7b9fc019bf3f61ebf14cf7c9cdca79bcb2a4219195371c02268f11" default)))
 '(package-selected-packages (quote (humanoid-themes magit))))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(region ((t (:background "#CAEBB8" :foreground "#ffffff" :box nil :weight bold))))
 '(secondary-selection ((t (:background "#C1C9BD")))))

;; #################################
;; Custom Configuration
;; #################################

;; remove start screen
(setq inhibit-startup-screen t)

;; remove tool bar
(tool-bar-mode -1)

;; set theme
(load-theme 'humanoid-light t)

;; #################################
;; Magit Setup
;; #################################
(require 'magit)

;; custom keyboard shortcuts
(global-set-key (kbd "M-u") 'previous-buffer)
(global-set-key (kbd "M-o") 'next-buffer)
(global-set-key (kbd "M-i") 'previous-line)
(global-set-key (kbd "M-k") 'next-line)
(global-set-key (kbd "M-q") 'magit-status)
(global-set-key (kbd "M-l") 'magit-log-all-branches)
(global-set-key (kbd "M-d") 'magit-diff-dwim)
(global-set-key (kbd "M-r") 'magit-list-repositories)

;; open Magit buffer in the main window - Do not just split them
(defun magit-display-buffer-same-window (buffer)
  (display-buffer
   buffer '(display-buffer-same-window)))

(setq magit-display-buffer-function 'magit-display-buffer-same-window)

;; setup columns to show in repository list buffer
(setq magit-repolist-columns
      '(("Name"    25 magit-repolist-column-ident ())
        ("D"        1 magit-repolist-column-dirty ())
        ("Path"    99 magit-repolist-column-path ())))

;; setup repository list for fast switching
(setq magit-repository-directories
        '(("~/local_disk/everything_in_one_place"  . 0)
          ("~/local_disk/Video_Lectures" . 10)
          ("~/.config" . 0)
          ("~/local_disk/c++/" . 3)))

;; opening screen
;; if emacs is opened in a repo folder, call magit-status
;; otherwise show list of repositories to open
(defvar init-error nil "")
(condition-case the-error
    (progn
      ;; Do the dangerous stuff here.
      (magit-status))
  (error
   ;; This is only evaluated if there's an error.
   (magit-list-repositories)))

