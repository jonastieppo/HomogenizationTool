import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MaterialdataComponent } from './materialdata.component';

describe('MaterialdataComponent', () => {
  let component: MaterialdataComponent;
  let fixture: ComponentFixture<MaterialdataComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MaterialdataComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MaterialdataComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
