;;; vue-mode-autoloads.el --- automatically extracted autoloads
;;
;;; Code:
(add-to-list 'load-path (or (file-name-directory #$) (car load-path)))

;;;### (autoloads nil "vue-mode" "vue-mode.el" (23043 53334 142546
;;;;;;  286000))
;;; Generated autoloads from vue-mode.el

(autoload 'vue-mode-edit-all-indirect "vue-mode" "\
Open all subsections with `edit-indirect-mode' in seperate windows.
If KEEP-WINDOWS is set, do not delete other windows and keep the root window
open in a window.

\(fn &optional KEEP-WINDOWS)" t nil)

(autoload 'vue-mode "vue-mode" "\


\(fn)" t nil)

(setq mmm-global-mode 'maybe)

(add-to-list 'auto-mode-alist '("\\.vue\\'" . vue-mode))

;;;***

;; Local Variables:
;; version-control: never
;; no-byte-compile: t
;; no-update-autoloads: t
;; End:
;;; vue-mode-autoloads.el ends here
