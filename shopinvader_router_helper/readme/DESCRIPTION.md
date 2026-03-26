Base helper for all shopinvader routers.

## Simple Usage

The helper can be used as-is for a simple inheritable router logic:

```python

@router.get("/name-type/{name}/{type}")
async def name_type(
    name: str, type: str, env: Annotated[Environment, Depends(odoo_env)]
  ):
  helper = env["shopinvader.router.name_type.helper"].new(dict(
      name=name, type=type
  ))
  return helper.fetch_data()


class RouterHelperNameType(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader.router.name_type.helper"

    name = fields.Char()
    type = fields.Selection(
        selection=[("type_1", "Type 1"), ("type_2", "Type 2")],
        default="type_1",
    )

    def fetch_data(self):
      return requests.get("https://my.api/{}/{}".format(self.name, self.type))
```

## CRUD Usage

The helper can also be used to implement a full CRUD logic.
For that, you need to define the model to use and the domain to restrict the records operations on.

```python
@router.post("/items/")
async def create_item(
    item: ItemCreate, env: Annotated[Environment, Depends(odoo_env)]
  ):
  helper = env["shopinvader.router.item.helper"].new()
  return helper.create(item.dict())

@router.get("/items/")
async def read_items(
    env: Annotated[Environment, Depends(odoo_env)]
  ):
  helper = env["shopinvader.router.item.helper"].new()
  return helper.search()

@router.get("/items/{item_id}")
async def read_item(
    item_id: int, env: Annotated[Environment, Depends(odoo_env)]
  ):
  helper = env["shopinvader.router.item.helper"].new()
  return helper.get(item_id)

@router.put("/items/{item_id}")
async def update_item(
    item_id: int, item: ItemUpdate, env: Annotated[Environment, Depends(odoo_env)]
  ):
  helper = env["shopinvader.router.item.helper"].new()
  return helper.write(item_id, item.dict())

@router.delete("/items/{item_id}")
async def delete_item(
    item_id: int, env: Annotated[Environment, Depends(odoo_env)]
  ):
  helper = env["shopinvader.router.item.helper"].new()
  return helper.unlink(item_id)

class RouterHelperItem(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader.router.item.helper"

    _model = "my.item.model"

    def _domain(self):
        domain = [('api_available', '=', True)]
        domain.append(('partner_id', '=', self.partner_id.id))
        return domain
```

## TODO

- Check helper usage with fastapi dependency injection system for cleaner code.
- More utils (pdf export, file handling, ...).
