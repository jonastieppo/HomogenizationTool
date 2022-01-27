import { Component, OnInit } from '@angular/core';

export interface Fiber {
  name: string;
  E1: number;
  E2: number;
  G12: number;
  G23: number;
  v12: number;
  v23: number;
  vf: number;
}

export interface Matrix {
  name: string;
  E1: number;
  v12: number;
}

const Matrix_example: Matrix[] = [
  {name: "Epoxy", E1: 10, v12: 1.0079}
];

const Fiber_example: Fiber[] = [
  {name: "Viynil Ester/Epoxy", E1: 10, E2: 1.0079, G12:10, G23:12, v12:0.3, v23:0.33, vf:0.57}
];

@Component({
  selector: 'app-materialdata',
  templateUrl: './materialdata.component.html',
  styleUrls: ['./materialdata.component.css']
})
export class MaterialdataComponent implements OnInit {
  
  displayedColumnsMatrix: string[] = ['name','E1','v12'];
  dataSourceMatrix = Matrix_example;

  displayedColumnsFiber: string[] = ['name','E1','E2', 'G12', 'G23', 'v12', 'v23', 'vf'];
  dataSourceFiber = Fiber_example;

  constructor() { }

  ngOnInit(): void {
  }

}
