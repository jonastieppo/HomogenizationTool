import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { flush } from '@angular/core/testing';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {MatButtonModule} from '@angular/material/button';


@Component({
  selector: 'app-modelcreation',
  templateUrl: './modelcreation.component.html',
  styleUrls: ['./modelcreation.component.css']
})
export class ModelcreationComponent implements OnInit {

  firstFormGroup!: FormGroup;
  secondFormGroup!: FormGroup;
  isEditable = false;
  clicked!: boolean;
  selected_fiber = 'op1';
  selected_matrix = 'op1';
  fibers: Array<string> = ["op1","op2","op3"]; //after the properties will be loaded from database
  matrix: Array<string> = ["op1","op2","op3"]; //after the properties will be loaded from database
  // items = ["op1","op2"]
  showFibersTable:boolean = false;
  showMatrixTable:boolean = false;
  showTexGen:boolean=false
  fileName:string = ""
  onFileSelected(event: any){
    const file:File = event.target.files[0];

          if (file) {

            this.fileName = file.name;

            const formData = new FormData();

            formData.append("thumbnail", file);

            const upload$ = this.http.post("/api/thumbnail-upload", formData);

            upload$.subscribe();
        }
    
  }

  showSelectedFibers(){
    this.showFibersTable=!this.showFibersTable;
    this.showMatrixTable=false;
    this.showTexGen=false;

  }

  showSelectedMatrix(){
    this.showMatrixTable=!this.showMatrixTable
    this.showFibersTable=false;
    this.showTexGen=false;
  }

  showSelectedTexgen(){
    this.showTexGen=!this.showTexGen
    this.showFibersTable=false;
    this.showMatrixTable=false;
  }
  constructor(private _formBuilder: FormBuilder, private http: HttpClient) {}

  ngOnInit() {
    this.firstFormGroup = this._formBuilder.group({
      firstCtrl: ['', Validators.required],
    });
    this.secondFormGroup = this._formBuilder.group({
      secondCtrl: ['', Validators.required],
    });
  }

}
