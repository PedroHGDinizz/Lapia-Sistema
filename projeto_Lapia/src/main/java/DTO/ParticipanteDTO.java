package DTO;

import java.util.List;

public record ParticipanteDTO(
        Long id,
        String nome,
        Integer idade,
        String sexo,
        String diagnostico,
        List<AvaliacaoResumoDTO> avaliacoes) {
}
