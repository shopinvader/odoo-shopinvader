===================
L10n_br_shopinvader
===================

Este módulo de  Api disponilizada uma rota para a procura de um cep
e também em seu retorno oferece a opção de cálculo de frete.

Configuration
=============

O cálculo de frete exige que algumas condições sejam atendidas:

* 1 - A moeda precisa estar devidamente configurada. Pois não pode haver uma venda em R$ e nas configurações estar US$.

* 2 - O cliente precisa ter o CEP a Cidade e o estado registrado em seu cadastro.


Usage
=====

Quando adicionar um preço fixo do valor do frete e depois mudar para
regras, primeiro certifique-se de que o campo preço fixo não ficou salvo
algum valor.

Caso o Cep passado no endpoint não encontrar nenhum Método de Envio
registrado com este CEP, então, o sistema retornará o Método de Envio
que estiver na sequência de prioridade.

Caso o Cep passado no endpoint for encontrado em vários Métodos de Envios
publicados, então, ele retornará uma lista com os Métodos de Envios.

Changelog
=========
