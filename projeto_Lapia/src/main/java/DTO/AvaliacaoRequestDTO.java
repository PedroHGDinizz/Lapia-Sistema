package DTO;

import java.util.List;

public record AvaliacaoRequestDTO(
        Long participanteId,
        String nomeEscala,        // campo novo
        List<RespostaItemDTO> respostas
) {}
