package DTO;

import com.br.pedro.projeto_Lapia.Model.Avaliacao;

import java.util.List;

public record ParticipanteDTO(
        Long id,
        String nome,
        Integer idade,
        List<AvaliacaoResumoDTO> avaliacoes) {
}
