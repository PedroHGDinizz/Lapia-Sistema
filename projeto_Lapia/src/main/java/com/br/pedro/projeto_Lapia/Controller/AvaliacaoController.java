package com.br.pedro.projeto_Lapia.Controller;

import DTO.AvaliacaoRequestDTO;
import DTO.AvaliacaoResumoDTO;
import com.br.pedro.projeto_Lapia.Model.Avaliacao;
import com.br.pedro.projeto_Lapia.Service.AvaliacaoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/avaliacoes")
public class AvaliacaoController {

    @Autowired
    private AvaliacaoService avaliacaoService;

    @PostMapping
    public ResponseEntity<AvaliacaoResumoDTO> criar(@RequestBody AvaliacaoRequestDTO dto) {
        AvaliacaoResumoDTO novaAvaliacao = avaliacaoService.salvar(dto);
        return ResponseEntity.status(HttpStatus.CREATED).body(novaAvaliacao);
    }
}