package main

import (
	"io/fs"

	koine "github.com/jrunic/koine"
)

// vaultFS é o embed.FS do vault, exportado pelo pacote raiz.
var vaultFS fs.FS = koine.VaultFS
