package com.br.pedro.projeto_Lapia.Service;

import DTO.AvaliacaoResumoDTO;
import DTO.ParticipanteDTO;
import com.br.pedro.projeto_Lapia.Model.Participante;
import com.br.pedro.projeto_Lapia.Repository.ParticipanteRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ParticipanteService {
    @Autowired
    private ParticipanteRepository participanteRepository;

    public ParticipanteDTO buscarPorId(Long id) {
        // 1. Busca a entidade original do banco
        Participante participante = participanteRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Participante não encontrado"));

        // 2. Converte a lista de Avaliacao para AvaliacaoResumoDTO
        List<AvaliacaoResumoDTO> avaliacoesDTO = participante.getAvaliacoes().stream()
                .map(avaliacao -> new AvaliacaoResumoDTO(
                        avaliacao.getId(),
                        avaliacao.getDataCriacao(),
                        avaliacao.getNomeEscala(),
                        avaliacao.getScore(),
                        null,
                        null
                ))
                .toList();

        // 3. Monta e retorna o ParticipanteDTO completo e sem loops
        return new ParticipanteDTO(
                participante.getId(),
                participante.getNome(),
                participante.getIdade(),
                avaliacoesDTO
        );
    }
}
