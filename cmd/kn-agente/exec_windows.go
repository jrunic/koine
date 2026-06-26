//go:build windows

package main

import (
	"fmt"
	"os"
	"os/exec"
)

// lancarClienteImpl no Windows usa exec.Command (syscall.Exec indisponível).
// Onda 2 revisará TTY handling para Copilot CLI se necessário.
func lancarClienteImpl(cliente, pastaAbs string, envVarsExtras map[string]string, extraArgs []string) error {
	binPath, err := exec.LookPath(cliente)
	if err != nil {
		return fmt.Errorf("cliente %q não encontrado no PATH — instale e tente novamente", cliente)
	}
	argv := append([]string{binPath}, extraArgs...)
	cmd := exec.Command(argv[0], argv[1:]...)
	cmd.Dir = pastaAbs
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Env = os.Environ()
	for k, v := range envVarsExtras {
		cmd.Env = append(cmd.Env, k+"="+v)
	}
	return cmd.Run()
}
