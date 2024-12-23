#!/bin/bash
cd '/Volumes/Datos/DESARROLLO PERSONAL/PROGRAMAR APLICACIONES WEB/Perfeccionar Python/Proyectos Python/Trading Bot Exchange/exchange/future/estrategias/infinity'
ssh -i "clave_pen_ec2_01.pem" ubuntu@ec2-15-228-57-72.sa-east-1.compute.amazonaws.com "cd exchange
        source entorno/bin/activate
        python3 future/estrategias/infinity/infinity_2.0.py"
