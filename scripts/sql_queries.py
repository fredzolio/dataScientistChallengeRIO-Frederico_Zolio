def query_chamados_abertos_dia(data):
    return f"""
    SELECT COUNT(*) AS total_chamados
    FROM `datario.adm_central_atendimento_1746.chamado`
    WHERE DATE(data_inicio) = '{data}';
    """

def query_tipo_mais_chamados_dia(data):
    return f"""
    SELECT tipo, COUNT(*) AS total
    FROM `datario.adm_central_atendimento_1746.chamado`
    WHERE DATE(data_inicio) = '{data}'
    GROUP BY tipo
    ORDER BY total DESC
    LIMIT 1;
    """

def query_bairros_mais_chamados_dia(data):
    return f"""
    SELECT b.nome AS bairro, COUNT(c.id_chamado) AS numero_chamados, b.geometry_wkt
    FROM `datario.adm_central_atendimento_1746.chamado` c
    JOIN `datario.dados_mestres.bairro` b ON c.id_bairro = b.id_bairro
    WHERE DATE(c.data_inicio) = '{data}'
    GROUP BY b.nome, b.geometry_wkt
    ORDER BY numero_chamados DESC
    LIMIT 3;
    """

def query_subprefeitura_mais_chamados_dia(data):
    return f"""
    SELECT b.subprefeitura, COUNT(c.id_chamado) AS total
    FROM `datario.adm_central_atendimento_1746.chamado` c
    JOIN `datario.dados_mestres.bairro` b ON c.id_bairro = b.id_bairro
    WHERE DATE(c.data_inicio) = '{data}'
    GROUP BY b.subprefeitura
    ORDER BY total DESC
    LIMIT 1;
    """

def query_chamados_sem_bairro_subprefeitura(data):
    return f"""
    SELECT COUNT(*) AS total
    FROM `datario.adm_central_atendimento_1746.chamado` c
    LEFT JOIN `datario.dados_mestres.bairro` b ON c.id_bairro = b.id_bairro
    WHERE DATE(c.data_inicio) = '{data}'
    AND (b.nome IS NULL OR b.subprefeitura IS NULL);
    """

def query_perturbacao_sossego_chamados(data_inicio, data_fim):
    return f"""
    SELECT COUNT(*) AS total
    FROM `datario.adm_central_atendimento_1746.chamado`
    WHERE subtipo = 'Perturbação do sossego'
    AND data_inicio BETWEEN '{data_inicio}' AND '{data_fim}';
    """

def query_chamados_durante_eventos():
    return """
    SELECT c.*, e.evento
    FROM `datario.adm_central_atendimento_1746.chamado` c
    JOIN `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` e
      ON DATE(c.data_inicio) BETWEEN e.data_inicial AND e.data_final
    WHERE c.subtipo = 'Perturbação do sossego'
    AND e.evento IN ('Reveillon', 'Carnaval', 'Rock in Rio');
    """

def query_chamados_por_evento():
    return """
    SELECT e.evento, COUNT(*) AS total
    FROM `datario.adm_central_atendimento_1746.chamado` c
    JOIN `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` e
      ON DATE(c.data_inicio) BETWEEN e.data_inicial AND e.data_final
    WHERE c.subtipo = 'Perturbação do sossego'
    GROUP BY e.evento;
    """

def query_media_diaria_por_evento():
    return """
    SELECT evento, AVG(chamados_por_dia) AS media_diaria
    FROM (
      SELECT e.evento, DATE(c.data_inicio) AS dia, COUNT(*) AS chamados_por_dia
      FROM `datario.adm_central_atendimento_1746.chamado` c
      JOIN `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` e
        ON DATE(c.data_inicio) BETWEEN e.data_inicial AND e.data_final
      WHERE c.subtipo = 'Perturbação do sossego'
      GROUP BY e.evento, DATE(c.data_inicio)
    )
    GROUP BY evento
    ORDER BY media_diaria DESC;
    """

def query_comparacao_media_diaria(data_inicio, data_fim):
    return f"""
    WITH media_total AS (
      SELECT AVG(chamados_por_dia) AS media_diaria_total
      FROM (
        SELECT DATE(data_inicio) AS dia, COUNT(*) AS chamados_por_dia
        FROM `datario.adm_central_atendimento_1746.chamado`
        WHERE subtipo = 'Perturbação do sossego'
        AND data_inicio BETWEEN '{data_inicio}' AND '{data_fim}'
        GROUP BY DATE(data_inicio)
      )
    )
    
    , media_eventos AS (
      SELECT evento, AVG(chamados_por_dia) AS media_diaria_evento
      FROM (
        SELECT e.evento, DATE(c.data_inicio) AS dia, COUNT(*) AS chamados_por_dia
        FROM `datario.adm_central_atendimento_1746.chamado` c
        JOIN `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` e
          ON DATE(c.data_inicio) BETWEEN e.data_inicial AND e.data_final
        WHERE c.subtipo = 'Perturbação do sossego'
        GROUP BY e.evento, DATE(c.data_inicio)
      )
      GROUP BY evento
    )
    
    SELECT evento, me.media_diaria_evento, mt.media_diaria_total
    FROM media_eventos me, media_total mt;
    """
