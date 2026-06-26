//go:build !windows

package main

import (
	"fmt"
	"os"
	"os/exec"
	"syscall"
)

// lancarClienteImpl substitui o processo atual pelo cliente via syscall.Exec.
// O cliente herda o TTY real e o process group do pai — Ctrl+C funciona corretamente.
// envVarsExtras é adicionado ao os.Environ() antes do Exec.
func lancarClienteImpl(cliente, pastaAbs string, envVarsExtras map[string]string, extraArgs []string) error {
	binPath, err := exec.LookPath(cliente)
	if err != nil {
		return fmt.Errorf("cliente %q não encontrado no PATH — instale e tente novamente", cliente)
	}
	if err := os.Chdir(pastaAbs); err != nil {
		return fmt.Errorf("cd %s: %w", pastaAbs, err)
	}
	env := os.Environ()
	for k, v := range envVarsExtras {
		env = append(env, k+"="+v)
	}
	argv := append([]string{cliente}, extraArgs...)
	return syscall.Exec(binPath, argv, env)
}
