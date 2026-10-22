package com.br.pedro.projeto_Lapia.Service;

import DTO.AvaliacaoRequestDTO;
import DTO.AvaliacaoResumoDTO;
import com.br.pedro.projeto_Lapia.Model.Avaliacao;
import com.br.pedro.projeto_Lapia.Model.Participante;
import com.br.pedro.projeto_Lapia.Model.Respostas;
import com.br.pedro.projeto_Lapia.Repository.AvaliacaoRepository;
import com.br.pedro.projeto_Lapia.Repository.ParticipanteRepository;
import com.br.pedro.projeto_Lapia.Repository.RespostasRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class AvaliacaoService {

    @Autowired
    private AvaliacaoRepository avaliacaoRepository;

    @Autowired
    private ParticipanteRepository participanteRepository;

    @Autowired
    private RespostasRepository respostasRepository;

    public AvaliacaoResumoDTO salvar(AvaliacaoRequestDTO dto) {

        // 1. Busca o participante
        Participante participante = participanteRepository.findById(dto.participanteId())
                .orElseThrow(() -> new RuntimeException("Participante não encontrado"));

        // 2. Calcula os scores do SNAP-IV
        // Questões 1-9: déficit de atenção | Questões 10-18: hiperatividade
        List<Integer> valoresDesatencao = dto.respostas().stream()
                .filter(r -> r.numeroQuestao() >= 1 && r.numeroQuestao() <= 9)
                .map(r -> r.valor())
                .toList();

        List<Integer> valoresHiperatividade = dto.respostas().stream()
                .filter(r -> r.numeroQuestao() >= 10 && r.numeroQuestao() <= 18)
                .map(r -> r.valor())
                .toList();

        double mediaDesatencao = valoresDesatencao.stream()
                .mapToInt(Integer::intValue).average().orElse(0.0);

        double mediaHiperatividade = valoresHiperatividade.stream()
                .mapToInt(Integer::intValue).average().orElse(0.0);

        int scoreFinal = dto.respostas().stream()
                .mapToInt(r -> r.valor()).sum();

        // 3. Cria e salva a Avaliacao
        Avaliacao avaliacao = new Avaliacao();
        avaliacao.setParticipante(participante);
        avaliacao.setDataCriacao(LocalDateTime.now());
        avaliacao.setScore(scoreFinal);
        avaliacao.setNomeEscala(dto.nomeEscala());
        Avaliacao avaliacaoSalva = avaliacaoRepository.save(avaliacao);

        // 4. Cria e salva cada Resposta vinculada à avaliação
        List<Respostas> respostasSalvas = dto.respostas().stream().map(item -> {
            Respostas r = new Respostas();
            r.setNumeroQuestao(item.numeroQuestao());
            r.setValor(item.valor());
            r.setAvaliacao(avaliacaoSalva);
            return r;
        }).toList();

        respostasRepository.saveAll(respostasSalvas);


        // 5. Retorna o DTO de resumo com os scores calculados
        return new AvaliacaoResumoDTO(
                avaliacaoSalva.getId(),
                avaliacaoSalva.getDataCriacao(),
                avaliacaoSalva.getNomeEscala(),   // novo
                scoreFinal,
                mediaDesatencao,
                mediaHiperatividade
        );
    }
}