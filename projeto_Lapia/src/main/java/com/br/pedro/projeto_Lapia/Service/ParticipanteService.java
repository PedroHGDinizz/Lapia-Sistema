package com.br.pedro.projeto_Lapia.Service;

import DTO.AvaliacaoResumoDTO;
import DTO.ParticipanteDTO;
import com.br.pedro.projeto_Lapia.Model.Participante;
import com.br.pedro.projeto_Lapia.Model.Respostas;
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

        // 2. Converte a lista de Avaliacao para AvaliacaoResumoDTO calculando as médias do SNAP-IV
        List<AvaliacaoResumoDTO> avaliacoesDTO = participante.getAvaliacoes().stream()
                .map(avaliacao -> {
                    Double mediaDesatencao = null;
                    Double mediaHiperatividade = null;

                    if ("SNAP-IV".equals(avaliacao.getNomeEscala()) && avaliacao.getRespostas() != null && !avaliacao.getRespostas().isEmpty()) {
                        double des = avaliacao.getRespostas().stream()
                                .filter(r -> r.getNumeroQuestao() != null && r.getNumeroQuestao() >= 1 && r.getNumeroQuestao() <= 9)
                                .mapToInt(Respostas::getValor)
                                .average()
                                .orElse(0.0);

                        double hip = avaliacao.getRespostas().stream()
                                .filter(r -> r.getNumeroQuestao() != null && r.getNumeroQuestao() >= 10 && r.getNumeroQuestao() <= 18)
                                .mapToInt(Respostas::getValor)
                                .average()
                                .orElse(0.0);

                        // Arredonda para 2 casas decimais
                        mediaDesatencao = Math.round(des * 100.0) / 100.0;
                        mediaHiperatividade = Math.round(hip * 100.0) / 100.0;
                    }

                    return new AvaliacaoResumoDTO(
                            avaliacao.getId(),
                            avaliacao.getDataCriacao(),
                            avaliacao.getNomeEscala(),
                            avaliacao.getScore(),
                            mediaDesatencao,
                            mediaHiperatividade
                    );
                })
                .toList();

        // 3. Monta e retorna o ParticipanteDTO completo com sexo e diagnostico
        return new ParticipanteDTO(
                participante.getId(),
                participante.getNome(),
                participante.getIdade(),
                participante.getSexo(),
                participante.getDiagnostico(),
                avaliacoesDTO
        );
    }
}