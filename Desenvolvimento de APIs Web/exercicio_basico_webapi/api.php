<?php
    require_once('conexao.php');

    function getFromCodigo($conexao, $codigo = null) {
        /*utilizando $codigo como parâmetro opcional, conseguimos usar esta função
        tanto para códigos recebidos via GET quanto via corpo de requisição, como
        em operações PUT.*/
        if (isset($_GET['codigo']) || isset($codigo)){
                $codigo = isset($codigo) ? (int) $codigo : (int) $_GET['codigo'];
                $sql = "SELECT * FROM cliente WHERE codigo = :codigo";

                $stmt = $conexao->prepare($sql);
                $stmt->bindParam(':codigo', $codigo);
                $stmt->execute();
        } else {
            $stmt = $conexao->query("SELECT * FROM cliente");
        }

        return $stmt->fetchAll(PDO::FETCH_ASSOC);        
    }

    $method = $_SERVER['REQUEST_METHOD'];
    $campos_bd = array('codigo', 'nome_completo', 'idade', 'telefone', 'email', 'foto');

    switch ($method) {
        case "GET":
            $clientes = getFromCodigo($conexao);
            header('Content-Type: application/json');
            echo json_encode($clientes);

            break;
        case "POST":
            $dados = json_decode(file_get_contents("php://input"), true);
            header('Content-Type: application/json');

            foreach ($campos_bd as $campo) {
                if (empty($dados[$campo]) && $campo !== 'foto' && $campo !== 'codigo') {
                    http_response_code(400);
                    echo json_encode(['error' => "O campo " . $campo . " é obrigatório!"]);
                    exit();
                }
            }

            $sql = "INSERT INTO cliente(nome_completo, idade, telefone, email, foto)
                    VALUES (:nome_completo, :idade, :telefone, :email, :foto)";
            
            $foto = isset($dados['foto']) ? $dados['foto'] : null;
            
            $stmt = $conexao->prepare($sql);
            $stmt->bindParam(':nome_completo', $dados['nome_completo']);
            $stmt->bindParam(':idade', $dados['idade']);
            $stmt->bindParam(':telefone', $dados['telefone']);
            $stmt->bindParam(':email', $dados['email']);
            $stmt->bindParam(':foto', $foto);
            $stmt->execute();

            $codigo = $conexao->lastInsertId();
            http_response_code(201);

            echo json_encode([
                'codigo' => $codigo,
                'nome_completo' => $dados['nome_completo'],
                'idade' => $dados['idade'],
                'telefone' => $dados['telefone'],
                'email' => $dados['email'],
                'foto' => $foto
            ]);

            break;
        case "PUT":
            /*a lógica utilizada no exercício em sala era a de que, para atualizar
            os dados de um registro identificado por código, todos os campos deveriam
            ser fornecidos. porém, pelo fato de que acredito que seja mais realista
            considerar que, na maioria das vezes, os ajustes feitos serão localizados
            (um campo específico ao invés de todos), farei uma validação menos restritiva.
            */
            $dados = json_decode(file_get_contents("php://input"), true);
            header('Content-Type: application/json');

            if (isset($dados['codigo'])) {
                $registroOriginal = getFromCodigo($conexao, $dados['codigo']);

                foreach ($campos_bd as $campo) {
                    if (!isset($dados[$campo])) {
                        /*acessando o índice 0 porque getFromCodigo retorna um array
                        independente da quantidade de registros do resultado*/
                        $dados[$campo] = $registroOriginal[0][$campo];
                    }
                }
            } else {
                http_response_code(400);
                echo json_encode(['error' => "O campo codigo é obrigatório!"]);
                exit();
            }

            $sql = "UPDATE cliente SET
                    nome_completo = :nome_completo,
                    idade = :idade,
                    telefone = :telefone,
                    email = :email,
                    foto = :foto
                    WHERE codigo = :codigo";
            $stmt = $conexao->prepare($sql);
            foreach ($campos_bd as $campo) {
                $stmt->bindParam(":$campo", $dados[$campo]);
            }
            $stmt->execute();

            http_response_code(200);
            echo json_encode([
                'codigo' => $dados['codigo'],
                'nome_completo' => $dados['nome_completo'],
                'idade' => $dados['idade'],
                'telefone' => $dados['telefone'],
                'email' => $dados['email'],
                'foto' => $dados['foto']
            ]);
            /*
            OBS: pela validação ser menos restritiva, caso seja enviado um JSON
            com campos que não existem no banco de dados, a operação PUT ainda será
            realizada, mas utilizando todos os mesmos dados que já estão no BD (ou seja,
            nada muda de verdade). é possível verificar as chaves do corpo da requisição
            para negar arquivos JSON com campos inválidos, mas não julguei ser necessário
            para os propósitos deste exercício.
            */

            break;
        case "DELETE":
            header('Content-Type: application/json');

            if (isset($_GET['codigo'])) {
                $sql = "DELETE FROM cliente WHERE codigo = :codigo";
                $stmt = $conexao->prepare($sql);
                $stmt->bindParam(':codigo', $_GET['codigo']);
                $stmt->execute();
                http_response_code(204);
                echo json_encode(["success" => true]);
            } else {
                http_response_code(400);
                echo json_encode(['error' => "O campo codigo é obrigatório!"]);
                exit();
            }

            break;
    }

?>