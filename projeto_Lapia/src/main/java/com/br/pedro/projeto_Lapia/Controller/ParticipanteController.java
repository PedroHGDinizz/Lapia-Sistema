package com.br.pedro.projeto_Lapia.Controller;

import com.br.pedro.projeto_Lapia.Model.Participante;
import com.br.pedro.projeto_Lapia.Repository.ParticipanteRepository;
import com.br.pedro.projeto_Lapia.Service.ParticipanteService;
import DTO.ParticipanteDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/participantes")
public class ParticipanteController {

    @Autowired
    private ParticipanteService participanteService;

    @Autowired
    private ParticipanteRepository participanteRepository;

    @GetMapping("/{id}")
    public ResponseEntity<ParticipanteDTO> buscarPorId(@PathVariable Long id) {
        ParticipanteDTO dto = participanteService.buscarPorId(id);
        return ResponseEntity.ok(dto);
    }

    @GetMapping
    public ResponseEntity<List<ParticipanteDTO>> listarTodos() {
        List<Participante> todos = participanteRepository.findAll();
        List<ParticipanteDTO> dtos = todos.stream()
                .map(p -> participanteService.buscarPorId(p.getId()))
                .toList();
        return ResponseEntity.ok(dtos);
    }

    @PostMapping
    public ResponseEntity<Participante> criar(@RequestBody Participante participante) {
        Participante salvo = participanteRepository.save(participante);
        return ResponseEntity.status(HttpStatus.CREATED).body(salvo);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deletar(@PathVariable Long id) {
        participanteRepository.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}