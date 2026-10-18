<?php

$host = "localhost";
$port = 3306;
$db = "ep1_webapi";
$user = "root";
$password = "";

try {
    $conexao = new PDO(
        "mysql:host=$host;port=$port;dbname=$db",
        $user,
        $password
    );
    $conexao->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch(PDOException $e) {
    echo "Erro na conexão: " . $e->getMessage();
    exit();
}

?>