import React, { useState, useRef, useEffect } from 'react';
import { Button, Form, FormControl, FormGroup } from 'react-bootstrap';
import {mapRadarImages, Position} from './extra/Interfaces';
import FormSelect from 'react-bootstrap/FormSelect';
import './editor.css';
import './styles/main.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import {grenadeSides, grenadeTypes, maps} from "./extra/enums";


const difficulties = [1, 2, 3];

function Admin() {
  const isClickPositionHandleRef = useRef(false);

  const [selectedMap, setSelectedMap] = useState<string>("MIRAGE");
  const [grenadeType, setGrenadeType] = useState<string>("HE");
  const [side, setSide] = useState<string>("CT");
  const [difficult, setDifficult] = useState<number>(1);
  const [positionList, setPositionList] = useState<Position[]>([]);
  const [additionalInfo, setAdditionalInfo] = useState<string>("");
  const [isInsta, setIsInsta] = useState<boolean>(false);
  const [initialName, setInitialName] = useState<string>("");
  const [initialId, setInitialId] = useState<number>(0);
  const [finalId, setFinalId] = useState<number>(0);
  const [finalName, setFinalName] = useState<string>("");
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [keyCombos, setKeyCombos] = useState<{ id: number; text: string }[]>([]);
  const [selectedComboId, setSelectedComboId] = useState<number | null>(null);
  const [isCursorActive, setIsCursorActive] = useState<boolean>(false);
  const [activeCursor, setActiveCursor] = useState<'initial' | 'final' | null>(null);
  const [finalTop, setFinalTop] = useState<number>(0);
  const [finalLeft, setFinalLeft] = useState<number>(0);
  const [initialTop, setInitialTop] = useState<number>(0);
  const [initialLeft, setInitialLeft] = useState<number>(0);
  const [id, setID] = useState<number|null>(null);
  const [isCustomCombo, setIsCustomCombo] = useState(false);
  const [customComboText, setCustomComboText] = useState('');
  const [draggingPoint, setDraggingPoint] = useState<'initial' | 'final' | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [bestMinute, setBestMinute] = useState<number | null>(null);
  const [bestSecond, setBestSecond] = useState<number | null>(null);

  const initialRef = useRef<HTMLInputElement>(null);
  const finalRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const fetchAdminData = async () => {
      const token = localStorage.getItem("access_token");

      const responseDataForForm = await fetch(`https://cs-education.ru/api/admin/get_data?map_name=${selectedMap}`, {
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        }
      });

      if (responseDataForForm.status !== 401) {
        const dataForForm = await responseDataForForm.json();
        setKeyCombos(dataForForm.key_combos || []);
        if (token) setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
      }
    }
    fetchAdminData();
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    setID(Number(params.get('id')));

    const fetchGrenades = async () => {
      try {
        const response = await fetch(`https://cs-education.ru/api/admin/get_data?map_name=${selectedMap}`, {
          headers: {"Authorization": `Bearer ${localStorage.getItem("access_token")}`}
        });
        const data = await response.json();
        setPositionList(data.map_positions);

        // Сброс координат и названий точек при смене карты
        setInitialLeft(0);
        setInitialTop(0);
        setFinalLeft(0);
        setFinalTop(0);
        setInitialName("");
        setFinalName("");
        setFinalId(0);
        setInitialId(0);
        isClickPositionHandleRef.current = false;
      } catch (error) {
        console.error('Ошибка при загрузке гранат:', error);
      }
    };
    fetchGrenades();
  }, [selectedMap]);

  const handleMapClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!activeCursor) return;
    if (isClickPositionHandleRef.current) {
      isClickPositionHandleRef.current = false;
      return;
    }

    const mapRect = (e.currentTarget as HTMLDivElement).getBoundingClientRect();
    const clickX = e.clientX - mapRect.left;
    const clickY = e.clientY - mapRect.top;

    const percentLeft = (clickX / mapRect.width) * 100;
    const percentTop = (clickY / mapRect.height) * 100;

    if (activeCursor === 'final') {
      setFinalLeft(percentLeft);
      setFinalTop(percentTop);
      setFinalName("");
      setFinalId(0);
    } else if (activeCursor === 'initial') {
      setInitialLeft(percentLeft);
      setInitialTop(percentTop);
      setInitialName("");
      setInitialId(0);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await fetch("https://cs-education.ru/api/admin/get_token", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
          username,
          password
        })
      });

      if (!response.ok) {
        throw new Error("Ошибка авторизации");
      }

      const data = await response.json();
      const token = data.access_token;

      localStorage.setItem("access_token", token);
      setIsAuthenticated(true);
    } catch (error) {
      alert("Ошибка авторизации. Проверьте логин/пароль");
      console.error("Login error:", error);
    }
  };

  const handleMouseDownOnPoint = (pointType: 'initial' | 'final') => {
    setDraggingPoint(pointType);
  };
  
  const handleMouseUp = () => {
    setDraggingPoint(null);
  };
  
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!draggingPoint) return;
  
    const mapRect = (e.currentTarget as HTMLDivElement).getBoundingClientRect();
    const moveX = e.clientX - mapRect.left;
    const moveY = e.clientY - mapRect.top;
  
    const percentLeft = (moveX / mapRect.width) * 100;
    const percentTop = (moveY / mapRect.height) * 100;
  
    if (draggingPoint === 'initial') {
      setInitialLeft(percentLeft);
      setInitialTop(percentTop);
    } else if (draggingPoint === 'final') {
      setFinalLeft(percentLeft);
      setFinalTop(percentTop);
    }
  };

  const handleSave = async () => {
    if (!initialName && initialRef.current) return initialRef.current.focus();
    if (!finalName && finalRef.current) return finalRef.current.focus();
    if (!id) {
      alert('Отсутствует id');
      return;
    }
    if (!finalLeft) {
      alert('Установите финальную позицию');
      return;
    }
    if (!initialLeft) {
      alert('Установите начальную позицию');
      return;
    }

    setIsLoading(true);

    let timingScore: number | undefined = undefined;
    if (bestMinute !== null && bestSecond !== null) {
      const total = bestMinute * 60 + bestSecond;
      const maxSeconds = 119;
      if (total <= maxSeconds) {
        timingScore = maxSeconds - total;
      } else {
        alert("Максимум: 1 минута 59 секунд");
        setIsLoading(false);
        return;
      }
    }

    let initial_position: unknown = {
      name: initialName,
      position: {
        top: initialTop,
        left: initialLeft,
        bottom: 100 - initialTop,
        right: 100 - initialLeft
      }
    };

    let final_position: unknown = {
      name: finalName,
      position: {
        top: finalTop,
        left: finalLeft,
        bottom: 100 - finalTop,
        right: 100 - finalLeft
      }
    };

    if (initialId) {
      initial_position = {
        id: initialId
      };
    }

    if (finalId) {
      final_position = {
        id: finalId
      };
    }

    const payload = {
      type: grenadeType,
      side,
      difficult,
      data: {
        additional_info: additionalInfo ? additionalInfo : undefined,
        is_insta: isInsta,
        best_timing: timingScore ? timingScore : undefined
      },
      id,
      map: selectedMap,
      initial_position: initial_position,
      final_position: final_position,
      key_combo: isCustomCombo
        ? { text: customComboText }
        : {
            id: selectedComboId
          },
    };

    try {
      const response = await fetch("https://cs-education.ru/api/grenade/add", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify(payload)
      });
      alert("Сохранено успешно!");
    } catch (error) {
      console.error("Ошибка при сохранении:", error);
      alert("Ошибка при сохранении!");
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="d-flex justify-content-center align-items-center editor-height_100 editor-width_100">
        <Form onSubmit={handleLogin} style={{ width: '300px' }}>
          <h4 className="mb-3">Авторизация</h4>
          <FormGroup className="mb-3">
            <Form.Label>Логин</Form.Label>
            <FormControl type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
          </FormGroup>
          <FormGroup className="mb-3">
            <Form.Label>Пароль</Form.Label>
            <FormControl type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </FormGroup>
          <Button type="submit" variant="primary" className="w-100">Войти</Button>
        </Form>
      </div>
    );
  }

  return (
    <div className="d-flex p-4 gap-4 editor-height_100 editor-width_100">
      {isLoading && (
            <div className="loader-overlay">
              <div className="spinner" />
            </div>
        )}
      <div>
        <FormGroup className="mb-3 w-50">
          <Form.Label>Выберите карту</Form.Label>
          <FormSelect value={selectedMap} onChange={(e) => setSelectedMap(e.target.value)}>
            {Object.values(maps).map((map) => (
              <option key={map} value={map}>{map}</option>
            ))}
          </FormSelect>
        </FormGroup>

        <div className="d-flex gap-2 mb-3">
          <Button
            variant={activeCursor === 'initial' ? "secondary" : "outline-secondary"}
            onClick={() => setActiveCursor(activeCursor === 'initial' ? null : 'initial')}
          >
            Установить начальную точку
          </Button>
          <Button
            variant={activeCursor === 'final' ? "secondary" : "outline-secondary"}
            onClick={() => setActiveCursor(activeCursor === 'final' ? null : 'final')}
          >
            Установить финальную точку
          </Button>
        </div>

        <div
          onClick={handleMapClick}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          className="mt-4 d-flex justify-content-center align-items-center"
          style={{
            aspectRatio: '1 / 1',
            width: '600px',
            backgroundColor: '#e9ecef',
            border: '1px solid',
            position: 'relative',
            cursor: isCursorActive ? 'crosshair' : 'default'
          }}
        >
          <img
            src={mapRadarImages[selectedMap]}
            alt={`Карта ${selectedMap}`}
            style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
          />
          {positionList.map((g, idx) => (
            <React.Fragment key={idx}>
              <div
                onClick={() => {
                  if (!activeCursor) return;

                  if (activeCursor === 'initial') {
                    setInitialTop(g.position.top);
                    setInitialLeft(g.position.left);
                    setInitialName(g.name);
                    setInitialId(g.id);
                  } else if (activeCursor === 'final') {
                    setFinalTop(g.position.top);
                    setFinalLeft(g.position.left);
                    setFinalName(g.name);
                    setFinalId(g.id);
                  }

                  isClickPositionHandleRef.current = true;
                }}
                style={{
                  border: '1px solid',
                  borderRadius: '50%',
                  backgroundColor: 'red',
                  position: 'absolute',
                  top: `${g.position.top}%`,
                  left: `${g.position.left}%`,
                  transform: 'translate(-50%, -50%)',
                  width: '2%',
                  height: '2%',
                  cursor: 'pointer',
                }}
              />
              <div
                onClick={() => {
                  if (!activeCursor) return;

                  if (activeCursor === 'initial') {
                    setInitialTop(g.position.top);
                    setInitialLeft(g.position.left);
                    setInitialName(g.name);
                    setInitialId(g.id);
                  } else if (activeCursor === 'final') {
                    setFinalTop(g.position.top);
                    setFinalLeft(g.position.left);
                    setFinalName(g.name);
                    setFinalId(g.id);
                  }

                  isClickPositionHandleRef.current = true;
                }}
                style={{
                  border: '1px solid',
                  borderRadius: '50%',
                  backgroundColor: 'red',
                  position: 'absolute',
                  top: `${g.position.top}%`,
                  left: `${g.position.left}%`,
                  transform: 'translate(-50%, -50%)',
                  width: '2%',
                  height: '2%',
                  cursor: 'pointer',
                }}
              />
            </React.Fragment>
          ))}
          {finalTop > 0 && finalLeft > 0 && (
            <div onMouseDown={() => handleMouseDownOnPoint('final')}
                style={{
                  border: '1px solid',
                  borderRadius: '50%',
                  backgroundColor: 'green',
                  position: 'absolute',
                  top: `${finalTop}%`,
                  left: `${finalLeft}%`,
                  width: '2%',
                  height: '2%',
                  transform: 'translate(-50%, -50%)',
                  zIndex: 10
            }} />
          )}
          {initialTop > 0 && initialLeft > 0 && (
            <div onMouseDown={() => handleMouseDownOnPoint('initial')}
                style={{
                  border: '1px solid',
                  borderRadius: '50%',
                  backgroundColor: 'green',
                  position: 'absolute',
                  top: `${initialTop}%`,
                  left: `${initialLeft}%`,
                  width: '2%',
                  height: '2%',
                  transform: 'translate(-50%, -50%)',
                  zIndex: 10
            }} />
          )}
        </div>
      </div>

      <div style={{ width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'baseline' }}>
          <FormGroup className="mb-3" style={{ marginRight: '12px' }}>
            <Form.Label>Тип гранаты</Form.Label>
            <FormSelect value={grenadeType} onChange={(e) => setGrenadeType(e.target.value)}>
              {Object.values(grenadeTypes).map(type => <option key={type}>{type}</option>)}
            </FormSelect>
          </FormGroup>
          <FormGroup className="mb-3">
            <Form.Label>Сторона</Form.Label>
            <FormSelect value={side} onChange={(e) => setSide(e.target.value)}>
              {Object.values(grenadeSides).map(s => <option key={s}>{s}</option>)}
            </FormSelect>
          </FormGroup>
        </div>

        <div style={{ display: 'flex', alignItems: 'baseline' }}>
          <FormGroup className="mb-3" style={{ marginRight: '12px' }}>
            <Form.Label>Сложность</Form.Label>
            <FormSelect value={difficult} onChange={(e) => setDifficult(Number(e.target.value))}>
              {difficulties.map(d => <option key={d}>{d}</option>)}
            </FormSelect>
          </FormGroup>
          <FormGroup className="mb-3">
            <Form.Label>Начальная позиция *</Form.Label>
            <FormControl ref={initialRef} type="text" placeholder="Имя позиции" value={initialName} onChange={(e) => setInitialName(e.target.value)} isInvalid={!initialName} />
          </FormGroup>
        </div>

        <div style={{ display: 'flex', alignItems: 'baseline' }}>
          <FormGroup className="mb-3"  style={{ marginRight: '12px' }}>
            <Form.Label>Комбинация клавиш *</Form.Label>
            <FormSelect
              value={isCustomCombo ? 'custom' : selectedComboId ?? ''}
              onChange={(e) => {
                const value = e.target.value;
                if (value === 'custom') {
                  setIsCustomCombo(true);
                  setSelectedComboId(null);
                } else {
                  setSelectedComboId(Number(value));
                  setIsCustomCombo(false);
                  setCustomComboText('');
                }
              }}
            >
              <option value="">Выберите комбинацию</option>
              {keyCombos.map(combo => (
                <option key={combo.id} value={combo.id}>{combo.text}</option>
              ))}
              <option value="custom">+ Добавить свою...</option>
            </FormSelect>
          </FormGroup>

          {isCustomCombo && (
            <FormGroup className="mb-3">
              <Form.Label>Своя комбинация</Form.Label>
              <FormControl
                type="text"
                value={customComboText}
                onChange={(e) => setCustomComboText(e.target.value)}
                placeholder="Введите новую комбинацию"
              />
            </FormGroup>
          )}
        </div>

        <FormGroup className="mb-3">
          <Form.Check 
            type="checkbox" 
            label="Моментальная граната (Insta)" 
            checked={isInsta} 
            onChange={(e) => setIsInsta(e.target.checked)} 
          />
        </FormGroup>

        <div style={{ display: 'flex', alignItems: 'baseline' }}>
          <FormGroup className="mb-3" style={{ marginRight: '12px' }}>
            <Form.Label>Финальная позиция *</Form.Label>
            <FormControl ref={finalRef} type="text" placeholder="Имя позиции" value={finalName} onChange={(e) => setFinalName(e.target.value)} isInvalid={!finalName} />
          </FormGroup>
        </div>

        <div style={{ display: 'flex', alignItems: 'baseline' }}>
          BestTiming (необязательно к заполнению)
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <FormGroup className="mb-3" style={{ marginRight: '12px' }}>
            <Form.Label className="text-muted small">Минуты</Form.Label>
            <FormControl
              type="number"
              min={0}
              max={1}
              value={bestMinute ?? ''}
              onChange={(e) => {
                let val = Number(e.target.value);
                if (isNaN(val)) val = 0;
                if (val > 1) val = 1;
                if (val < 0) val = 0;
                setBestMinute(val);

                // автоограничение секунд, если минута = 1
                if (val === 1 && bestSecond !== null && bestSecond > 59) {
                  setBestSecond(59);
                }
              }}
            />
          </FormGroup>

          <FormGroup className="mb-3">
            <Form.Label className="text-muted small">Секунды</Form.Label>
            <FormControl
              type="number"
              min={0}
              max={bestMinute === 1 ? 59 : 59}
              value={bestSecond ?? ''}
              onChange={(e) => {
                let val = Number(e.target.value);
                if (isNaN(val)) val = 0;
                const max = bestMinute === 1 ? 59 : 59;
                if (val > max) val = max;
                if (val < 0) val = 0;
                setBestSecond(val);
              }}
            />
          </FormGroup>
        </div>

        <div style={{ display: 'flex', alignItems: 'baseline' }}>
          <FormGroup className="mb-3">
            <Form.Label>Доп. информация</Form.Label>
            <FormControl
              as="textarea"
              rows={6}
              value={additionalInfo}
              onChange={(e) => setAdditionalInfo(e.target.value)}
              style={{ resize: 'vertical', width: '400px' }}
            />
          </FormGroup>
        </div>

        <Button variant="primary" onClick={handleSave}>Сохранить</Button>
      </div>
    </div>
  );
}

export default Admin;
