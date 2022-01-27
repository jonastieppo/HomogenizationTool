import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ModelcreationComponent } from './modelcreation.component';

describe('ModelcreationComponent', () => {
  let component: ModelcreationComponent;
  let fixture: ComponentFixture<ModelcreationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ModelcreationComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ModelcreationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
