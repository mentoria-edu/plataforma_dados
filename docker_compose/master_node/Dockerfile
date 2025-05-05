FROM imagem_base

# EXPOSE 8020 8030 8031 8032 8033 8088 9000 9083 9866 9868 9870 10000
COPY ./entrypoint.sh opt/entrypoint.sh
ENTRYPOINT ["bash", "-c", "bash /opt/entrypoint.sh"]