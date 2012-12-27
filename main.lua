
WIDTH = 800
HEIGHT = 600
debug_on = false

function love.load()

end
	
function love.draw()

end

function love.update(dt)
end

function love.keypressed(key, unicode)
	if key == "escape" then
		love.event.quit()
	elseif key == "tab" then
		debug_on = not debug_on
	end
end

function love.mousepressed(x, y, button)
end

function love.mousereleased(x, y, button)
end

