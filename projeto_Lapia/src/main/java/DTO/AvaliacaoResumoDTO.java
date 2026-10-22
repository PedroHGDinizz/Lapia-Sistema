package DTO;

import java.time.LocalDateTime;

public record AvaliacaoResumoDTO(
        Long id,
        LocalDateTime data,
        String nomeEscala,        // campo novo
        Integer pontuacaoSnapIV,
        Double mediaDesatencao,
        Double mediaHiperatividade
) {}
